"""Run the lisa2026 scoring container with GPU access via the Docker SDK.

Path B: instead of letting toil-cwl-runner `docker run lisa2026` directly
(which cannot attach a GPU on this old toil/cwltool version), this script
starts the scoring container through the Docker Python SDK and passes the GPU
exactly the way the test-phase run_docker.py does:

    device_requests=[DeviceRequest(count=-1, capabilities=[['gpu']])]
    runtime='nvidia'

It mounts the three inputs (prediction / reference / input zips) read-only,
mounts an output dir read-write, runs `lisa2026 --task1b -p .. -r .. -i .. -o ..`,
streams logs, and leaves results.json in the current working directory so the
CWL step can glob it.
"""
from __future__ import print_function

import argparse
import os
import shutil
import sys

import docker
from docker.types import DeviceRequest

# Same GPU request the test-phase runner uses: all GPUs, 'gpu' capability.
DEVICE_REQUESTS = [DeviceRequest(count=-1, capabilities=[["gpu"]])]

DOCKER_IMAGE = "lisa2026"
TASK_FLAG = "--task1b"


def main(args):
    client = docker.DockerClient(base_url="unix://var/run/docker.sock")

    cwd = os.getcwd()
    output_dir = os.path.join(cwd, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Stage the three inputs into dirs under cwd. cwd is the toil-managed
    # working dir, whose host<->container path mapping is consistent, so
    # volume mounts requested via the SDK resolve correctly under DinD.
    # (Mounting the toil-provided input paths directly does NOT work: those
    # paths exist inside this job container but not at the same location on
    # the host daemon that actually performs the mount.)
    pred_host = os.path.join(cwd, "in_pred")
    ref_host = os.path.join(cwd, "in_ref")
    inp_host = os.path.join(cwd, "in_input")
    for d in (pred_host, ref_host, inp_host):
        os.makedirs(d, exist_ok=True)

    pred_name = os.path.basename(args.prediction)
    ref_name = os.path.basename(args.reference)
    inp_name = os.path.basename(args.input)

    shutil.copy2(os.path.abspath(args.prediction), os.path.join(pred_host, pred_name))
    shutil.copy2(os.path.abspath(args.reference), os.path.join(ref_host, ref_name))
    shutil.copy2(os.path.abspath(args.input), os.path.join(inp_host, inp_name))

    volumes = {
        output_dir: {"bind": "/score_output", "mode": "rw"},
        pred_host: {"bind": "/in_pred", "mode": "ro"},
        ref_host: {"bind": "/in_ref", "mode": "ro"},
        inp_host: {"bind": "/in_input", "mode": "ro"},
    }

    pred_in_container = "/in_pred/" + pred_name
    ref_in_container = "/in_ref/" + ref_name
    inp_in_container = "/in_input/" + inp_name
    out_in_container = "/score_output/results.json"

    command = [
        TASK_FLAG,
        "-p", pred_in_container,
        "-r", ref_in_container,
        "-i", inp_in_container,
        "-o", out_in_container,
    ]

    print("Running scoring container with GPU:", DOCKER_IMAGE, command, flush=True)

    container = None
    try:
        container = client.containers.run(
            DOCKER_IMAGE,
            command=command,
            detach=True,
            volumes=volumes,
            runtime="nvidia",
            device_requests=DEVICE_REQUESTS,
            mem_limit="24g",
            stderr=True,
        )

        # Stream logs live.
        for line in container.logs(stream=True, follow=True):
            sys.stdout.write(line.decode("utf-8", "ignore"))
            sys.stdout.flush()

        result = container.wait()
        exit_code = result.get("StatusCode", 1)
    finally:
        if container is not None:
            try:
                container.remove(force=True)
            except Exception:
                pass

    # Bring results.json into the CWL working dir so the step can glob it.
    produced = os.path.join(output_dir, "results.json")
    if os.path.exists(produced):
        shutil.copy2(produced, os.path.join(cwd, "results.json"))
        print("results.json produced.", flush=True)
    else:
        print("ERROR: results.json was not produced by the scoring container.",
              file=sys.stderr)
        sys.exit(1)

    if exit_code != 0:
        print(f"Scoring container exited with code {exit_code}.", file=sys.stderr)
        sys.exit(exit_code)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--prediction", required=True, help="Prediction file/zip")
    parser.add_argument("-r", "--reference", required=True, help="Reference file/zip")
    parser.add_argument("-i", "--input", required=True, help="Input file/zip")
    parser.add_argument("-o", "--output_name", default="results.json",
                        help="Output JSON name (kept for CWL compatibility)")
    args = parser.parse_args()
    main(args)

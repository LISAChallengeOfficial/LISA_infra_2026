#!/usr/bin/env cwl-runner

cwlVersion: v1.0
class: CommandLineTool
label: Validate and return NII files

requirements:
  - class: InlineJavascriptRequirement
  - class: InitialWorkDirRequirement
    listing:
      - entryname: validate.py
        entry: |
          #!/usr/bin/env python
          import argparse
          import os
          import sys
          from glob import glob

          parser = argparse.ArgumentParser()
          parser.add_argument("-i", "--input_dir", required=True, help="Path to output directory")
          args = parser.parse_args()

          nii_files = glob(os.path.join(args.input_dir, "*.nii")) + glob(os.path.join(args.input_dir, "*.nii.gz"))

          if len(nii_files) == 0:
              print(f"❌ No .nii or .nii.gz files found in {args.input_dir}")
              sys.exit(1)
          else:
              print(f"✅ Found {len(nii_files)} .nii file(s):")
              for f in nii_files:
                  print(" -", os.path.basename(f))
              sys.exit(0)

inputs:
  - id: input_dir
    type: Directory

outputs:
  - id: found_files
    type: File[]
    outputBinding:
      glob: $(inputs.input_dir.path + "/*.nii*")

baseCommand: python
arguments:
  - valueFrom: validate.py
  - prefix: -i
    valueFrom: $(inputs.input_dir.path)

hints:
  DockerRequirement:
    dockerPull: python:3.9.1-slim-buster

#!/usr/bin/env cwl-runner
cwlVersion: v1.0
class: CommandLineTool
baseCommand: python3
requirements:
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing:
      - $(inputs.docker_script)
inputs:
  docker_script:
    type: File
    default:
      class: File
      location: score_docker.py
    inputBinding:
      position: 0
  task:
    type: string
    default: "--task1b"
  prediction:
    type: File
    inputBinding:
      position: 2
      prefix: -p
  reference:
    type: File
    inputBinding:
      position: 3
      prefix: -r
  input:
    type: File
    inputBinding:
      position: 4
      prefix: -i
  output_name:
    type: string
    inputBinding:
      position: 5
      prefix: -o
outputs:
- id: results
  type: File
  outputBinding:
    glob: results.json
- id: status
  type: string
  outputBinding:
    glob: results.json
    outputEval: $(JSON.parse(self[0].contents)['submission_status'])
    loadContents: true

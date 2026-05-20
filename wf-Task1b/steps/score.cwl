cwlVersion: v1.0
class: CommandLineTool
baseCommand: []

requirements:
  DockerRequirement:
    dockerPull: lisa2025v2
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing: []

inputs:
  task:
    type: string
    default: --task2a
    inputBinding:
      position: 1

  segs:
    type: File
    inputBinding:
      position: 2
      prefix: -p

  masks:
    type: File
    inputBinding:
      position: 3
      prefix: -g

  output_name:
    type: string
    inputBinding:
      position: 4
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




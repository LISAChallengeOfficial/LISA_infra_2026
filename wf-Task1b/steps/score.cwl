cwlVersion: v1.0
class: CommandLineTool
baseCommand: []

requirements:
  DockerRequirement:
    dockerPull: lisa2026
  InlineJavascriptRequirement: {}
  InitialWorkDirRequirement:
    listing: []

inputs:
  task:
    type: string
    default: --task1b
    inputBinding:
      position: 1

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




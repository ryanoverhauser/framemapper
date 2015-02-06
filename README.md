FrameMapper
===========
Approximates the frame location of words in a text file (script) by comparing them against an Adobe Premiere Speech Analysis tab-seperated value file. A .srt output can be generated based on line breaks in the input transcript.

###Usage

```python
from frame_mapper import FrameMapper

# Paths to our text files
script = 'data/SCRIPT_gp3267.txt'
analysis = 'data/ANALYSIS_gp3267.txt'

# Initialize the file mapper, passing file paths as arguments
fm = FrameMapper(script, analysis)

# Get srt output for the script
srt = fm.build_srt()
```
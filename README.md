FrameMapper
===========
This script approximates the frame location of words in a text file (script) by comparing them against an Adobe Premiere Speech Analysis tab-seperated value file.

###Usage

```python
from frame_mapper import FrameMapper

# Paths to our text files
script = 'data/SCRIPT_gp3267.txt'
analysis = 'data/ANALYSIS_gp3267.txt'

# Initialize the file mapper, passing file paths as arguments
fm = FrameMapper(script, analysis)

# Run the frame mapper
fm.map_phrases()

#Get the processed script word object array
words = fm.sWords
```
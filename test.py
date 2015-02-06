from frame_mapper import FrameMapper

# Paths to our text files
script = 'data/SCRIPT_sy0507.txt'
analysis = 'data/ANALYSIS_sy0507.txt'
# script = 'data/SCRIPT_gp3267.txt'
# analysis = 'data/ANALYSIS_gp3267.txt'

# Initialize the file mapper, passing file paths as arguments
fm = FrameMapper(script, analysis)

# Generate the srt file
srt = fm.build_srt()
print(srt)
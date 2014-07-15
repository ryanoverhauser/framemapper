from frame_mapper import FrameMapper

# sFile = 'data/SCRIPT_sy0507.txt'
# aFile = 'data/ANALYSIS_sy0507.txt'

# Paths to our text files
script = 'data/SCRIPT_gp3267.txt'
analysis = 'data/ANALYSIS_gp3267.txt'

# Initialize the file mapper, passing file paths as arguments
fm = FrameMapper(script, analysis)

# Run the frame mapper
fm.map_phrases(3)

#Get the processed script word object array
words = fm.sWords

print 'Script Word Count: ' + str(len(fm.sWords))
print 'Analysis Word Count: ' + str(len(fm.aWords))
print '============================================='
for i in range(len(words)):
	w = words[i]
	print str(i) + ')\t' + w.text + ' | ' + str(w.frame)
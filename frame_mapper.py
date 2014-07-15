import re
import csv
import codecs

# simple class to represent a single word
class Word(object):
	text = ""
	frame = False

	def __init__(self, text, frame):
		self.text = text
		self.frame = frame

# represents a matched phrase between two word arrays
class Phrase(object):
	sPos = 0
	aPos = 0
	length = 0

	def __init__(self, sPos, aPos, length):
		self.sPos = sPos
		self.aPos = aPos
		self.length = length

# the main class to handle mapping the frames between a source and analysis file
class FrameMapper(object):
	sFile = ""
	aFile = ""
	sWords = 0
	aWords = 0
	phraseLength = 3

	def __init__(self, sFile, aFile):
		self.sFile = sFile
		self.aFile = aFile
		self.sWords = self.parse_script_file()
		self.aWords = self.parse_analysis_file()

	# Parse script text into word array
	def parse_script_file(self):
		wordArray = []
		with codecs.open(self.sFile, encoding='utf-8') as script:
			s = script.read().upper() # read the file to a string
			s = self.replace_unicode_punctuation(s)
			words = re.sub("[^\w']", " ",  s).split() # convert non-alphanumeric to " " and then split
			for w in words:
				wordArray.append(Word(w, 0))
		return wordArray

	# Parse tab-separated-value analysis file into word array
	def parse_analysis_file(self):
		wordArray = []
		with open(self.aFile) as tsv:
			for line in csv.reader(tsv, delimiter="\t"):
				if line[2][0] != '<': # ignore silence and other tags
					wordArray.append(Word(line[2].upper(),int(line[0])))
		return wordArray

	# Find all matched phrases
	def map_phrases(self):
		minLength = self.phraseLength
		sW = []
		for w in (self.sWords):
			sW.append(w.text)
		aW = []
		for w in (self.aWords):
			aW.append(w.text)

		phrases = []
		i = 0
		while i < len(sW):
			phrase = self.find_phrase(sW, aW, i, minLength)
			if phrase:
				phrases.append(phrase)
				i += phrase.length
			else:
				i += 1

		self.assign_mapped_positions(phrases)
		self.approximate_unmapped_positions()

	# Assign frame positions based on matched phrases
	def assign_mapped_positions(self, phrases):
		for p in phrases:
			for i in range(0,p.length):
				self.sWords[p.sPos + i].frame = self.aWords[p.aPos + i].frame

	# Assign approximate frame position for unmapped words
	def approximate_unmapped_positions(self):
		spaces = [] # array to hold blocks of unmapped words
		i = 0
		while i < len(self.sWords):
			if not self.sWords[i].frame:
				count = 1
				while ((i + count) < len(self.sWords)) and (self.sWords[i + count].frame == False):
					count += 1
				space = [i, count]
				spaces.append(space)
				i += count
			else:
				i += 1
		for space in spaces:
			self.calculate_averages(space)

	# Calculate average spacing between group of words and assign frame positions
	def calculate_averages(self, s):
		prev = s[0] - 1
		next = s[0] + s[1]
		prevFrame = (self.sWords[prev].frame) if (prev >= 1) else 0
		nextFrame = (self.sWords[next].frame) if (next < len(self.sWords)) else 0
		avgLength = (nextFrame - prevFrame) / (s[1] + 1) if (nextFrame > prevFrame) else 0
		for i in range(s[0], (s[0] + s[1])):
			self.sWords[i].frame = prevFrame + ((i - s[0] + 1) * avgLength)

	# Search for longest phrase in target array given starting position in source array
	@staticmethod
	def find_phrase(sW, aW, pos, minLength):
		# find the index of each matching start word
		indices = [i for i, x in enumerate(aW) if x == sW[pos]]
		if not indices:
			return False # Word not found
		for i in indices:
			count = 0
			while ((i + count) < len(aW)) and (sW[pos + count] == aW[i + count]):
				count += 1
			if count >= minLength:
				return Phrase(pos, i, count)
		return False # No phrase found

	# convert left and right single and double quotation marks to ascii
	@staticmethod
	def replace_unicode_punctuation(string):
		uString = unicode(string)
		punctuation = { 0x2018:0x27, 0x2019:0x27, 0x201C:0x22, 0x201D:0x22 }
		return uString.translate(punctuation).encode('ascii', 'ignore')

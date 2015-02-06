import re
import csv
import codecs
from datetime import datetime, timedelta

# simple class to represent a single word
class Word(object):
	text = ""
	frame = False
	duration = False

	def __init__(self, text, frame, duration):
		self.text = text
		self.frame = frame
		self.duration = duration

# represents a matched phrase between two word arrays
class Phrase(object):
	sPos = 0
	aPos = 0
	length = 0

	def __init__(self, sPos, aPos, length):
		self.sPos = sPos
		self.aPos = aPos
		self.length = length

# represents a single subtitle line
class Title(object):
	text = ""
	start = False
	end = False

	def __init__(self, text):
		self.text = text

# the main class to handle mapping the frames between a source and analysis file
class FrameMapper(object):
	sFile = ""
	aFile = ""
	sWords = []
	aWords = []
	titles = []
	phraseLength = 3
	duration = 0

	def __init__(self, sFile, aFile):
		self.sFile = sFile
		self.aFile = aFile
		self.parse_script_file()
		self.parse_analysis_file()
		self.map_phrases()
		self.map_titles()

	# Parse script text into word array
	def parse_script_file(self):
		with codecs.open(self.sFile, encoding='utf-8') as script:
			s = script.read().upper() # read the file to a string
			words = re.sub("[^\w']", " ",  s).split() # convert non-alphanumeric to " " and then split
			for w in words:
				self.sWords.append(Word(w, 0, 0))
		with open(self.sFile) as f:
			lines = f.readlines()
		for l in lines:
			if l:
				self.titles.append(Title(l.strip()))

	# Parse tab-separated-value analysis file into word array
	def parse_analysis_file(self):
		with open(self.aFile) as tsv:
			for line in csv.reader(tsv, delimiter="\t"):
				self.duration = int(line[0]) # the last line will contain the duration for the whole clip
				if line[2][0] != '<': # ignore silence and other tags
					self.aWords.append(Word( line[2].upper(), int(line[0]), int(line[1]) ))

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
				self.sWords[p.sPos + i].duration = self.aWords[p.aPos + i].duration

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
			self.sWords[i].frame = prevFrame + round((i - s[0] + 1) * avgLength)
			self.sWords[i].duration = round(avgLength)

	# Calculate subtitle start and end positions
	def map_titles(self):

		for t in self.titles:
			pos = self.find_title(t)
			t.start = pos[0]
			t.end = pos[1]

		i = 0
		while i < len(self.titles):
			if i < (len(self.titles) - 1):
				if self.titles[i].end >= self.titles[i+1].start:
					self.titles[i].end = self.titles[i+1].start - 1
				else:
					sec = (self.titles[i].end - self.titles[i].start)
					target = round(len(self.titles[i].text) / 15 * 1000)
					self.titles[i].end = self.titles[i+1].start - 1 if (self.titles[i].start + target) >= self.titles[i+1].start else self.titles[i].start + target
			else:
				sec = (self.titles[i].end - self.titles[i].start)
				target = round(len(self.titles[i].text) / 15 * 1000)
				if (sec < target):
					self.titles[i].end = self.duration if (self.titles[i].start + target) > self.duration else self.titles[i].start + target

			i += 1

	# Find a subtitle in the script
	def find_title(self, title):

		phrase = title.text.upper()
		phrase = re.sub("[^\w']", " ",  phrase).split()

		bare = []
		for w in self.sWords:
			bare.append(w.text)

		i = 0
		while i < len(bare):
			if bare[i] == phrase[0]:
				endPos = i + len(phrase)
				if (bare[i:endPos] == phrase):
					start = self.sWords[i].frame
					end = self.sWords[endPos - 1].frame + self.sWords[endPos - 1].duration
			i += 1

		return [start, end]

	# Returns an srt for subtitles
	def build_srt(self):

		i = 0
		output = ''
		while i < len(self.titles):
			output += (str(i+1) + '\n' + self.format_timecode(self.titles[i].start) + ' --> ' + self.format_timecode(self.titles[i].end) + '\n' + self.titles[i].text) + '\n\n'
			i += 1

		# print(output)
		return output

	# Formats millisecond position for srt
	@staticmethod
	def format_timecode(msec):

		r = str(msec)[-3:]
		t = str(msec)[:-3]

		if not t:
			t = '0'

		sec = timedelta(seconds=int(t))
		d = datetime(1,1,1) + sec

		return d.strftime("%H:%M:%S") + ',' + r

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

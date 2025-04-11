#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os

#strings
from std.string import *

#lists
from std.list import *






# -------- TYPE DEF --------

#istr
class istr:
	def __init__(self, initStr, index=-1):
		self.index = index
		self.s     = initStr

	def get(self):
		return self.s[self.index]

	def set(self, value):
		self.s[self.index] = value

	def forward(self, step):
		if (self.index + step) >= len(self.s): #could not forward => ret True
			return True
		self.index += step
		return False

	def inc(self):
		return self.forward(1)

	def copy(self):
		return istr(self.s, self.index)

	def reachedEnd(self):
		return self.index == len(self.s)-1



#constants
PARSING_CTX__INVALID_FIRST_OPENNING        = -1 #these are to be cashted into map[unt_l,unt_l]
PARSING_CTX__INCONSISTENT_INCLUDER_PARSING = -2
PARSING_CTX__PEER_NOT_FOUND                = -3

#external actually but anyway
Term__TAB_LENGTH = 4

#parsing ctx object
class ParsingCtx:
	def __init__(self, filepath, content, resolveSymlinks=False):
		if resolveSymlinks:
			self.filepath = os.path.realpath(filepath)
		else:
			self.filepath = os.path.abspath(filepath)
		self.dirname    = os.path.dirname(self.filepath)
		self.filename   = os.path.basename(self.filepath)
		self.lineNbr    = 1
		self.colmNbr    = 0
		self.icontent   = istr(content)
		self.detectedLF = False

	#copy
	def copy(self, filepath=None, content=None):
		if filepath is None:
			filepath = self.filepath
		if content is None:
			content  = self.icontent.s
		newCtx = ParsingCtx(filepath, content)
		newCtx.icontent.index = self.icontent.index
		newCtx.lineNbr        = self.lineNbr
		newCtx.colmNbr        = self.colmNbr
		newCtx.detectedLF     = self.detectedLF
		return newCtx

	#print: temporarily made like this
	def toStr(self):
		return self.filepath + ":" + str(self.lineNbr) + ":" + str(self.colmNbr)



	#regular parsing
	def get(self):
		return self.icontent.get()

	def set(self, value):
		self.icontent.set(value)

	def inc(self):
		if self.icontent.inc(): #can't go further => can't go further
			return True

		#last character was a line feed => update line indicators
		if self.detectedLF:
			self.detectedLF = False
			self.lineNbr   += 1
			self.colmNbr    = 0

		#LF behavior
		if self.icontent.get() == '\n':
			self.detectedLF = True

		#regular behavior
		self.colmNbr += 1
		return False

	def forward(self, step):
		for s in range(step):
			if self.inc():
				return True
		return False

	def reachedEnd(self):
		return self.icontent.reachedEnd()

	def reset(self, newText=None):
		self.lineNbr    = 1
		self.colmNbr    = 0
		self.detectedLF = False
		if newText is not None:
			self.icontent.s     = newText
			self.icontent.index = -1



	#output
	def printLineIndicator(self):
		content = self.icontent.s

		#set beginning & end of line
		if self.icontent.index == -1: #invalid value (istr starting index)
			begIndex = 0
			endIndex = 0
		else:
			begIndex = self.icontent.index - (self.colmNbr-1)
			endIndex = self.icontent.index

		#that mean we are in the first line (cannot subtract colmNbr)
		if begIndex > endIndex:
			begIndex = 0

		#read to get real end of line
		while endIndex < len(content):
			if content[endIndex] == '\n':
				break
			endIndex += 1

		#print full line
		rawConcernedLine = str_sub(content, begIndex, endIndex)
		concernedLine    = str_expandTabs(rawConcernedLine, Term__TAB_LENGTH)
		print(concernedLine)

		#prepare position indicator
		positionIndex     = (Term__TAB_LENGTH-1) * rawConcernedLine.count('\t') + self.colmNbr - 1
		positionIndicator = ""
		for i in range(positionIndex):
			positionIndicator += '-'
		positionIndicator += '^'

		#print position indicator
		print(positionIndicator)



	#includers
	def getPairsUntilCorrespondingPeer(self, allowedPairs={'(':')', '[':']', '{':'}', '<':'>'}):

		#use local copy of context for precise error indication without affecting the original one
		localCtx = self.copy()
		c        = localCtx.get()
		if c in allowedPairs.keys():
			target = allowedPairs[c]

		#current position is not at a valid openning target
		else:
			return PARSING_CTX__INVALID_FIRST_OPENNING

		#prepare main pair (that can contain some other subPairs)
		resultPairs  = {} #map[unt_l,unt_l]
		initialIndex = self.icontent.index

		#read rest of the code taking into account every subPair
		subOpenings = [] #lst[chr]
		subIndexes  = [] #lst[unt_l]
		while not localCtx.inc():
			c = localCtx.get()

			#openning subPair
			if c in allowedPairs.keys():
				subOpenings.append(c)
				subIndexes.append(localCtx.icontent.index)

			#closing subPair
			elif c in allowedPairs.values():

				#no subzone remaining => looking for the targetted peer
				if lst_isEmpty(subOpenings):

					#found it
					if c == target:
						resultPairs[initialIndex] = localCtx.icontent.index #add main pair
						return resultPairs

					#inconsistency 1: closing too soon
					print("getPairsUntilCorrespondingPeer: Closing pair with '" + c + "' but expected '" + target + "' (at " + localCtx.toStr() + ").")
					return PARSING_CTX__INCONSISTENT_INCLUDER_PARSING

				#closing latest subPair
				latestOpening = lst_pop(subOpenings)
				latestIndex   = lst_pop(subIndexes)
				if c == allowedPairs[latestOpening]:
					resultPairs[latestIndex] = localCtx.icontent.index
					continue

				#inconsistency 2: unexpected peer
				print("getPairsUntilCorrespondingPeer: Closing pair with '" + c + "' but expected '" + allowedPairs[latestOpening] + "' (at " + localCtx.toStr() + ").")
				return PARSING_CTX__INCONSISTENT_INCLUDER_PARSING

		#peer not found
		return PARSING_CTX__PEER_NOT_FOUND



def lst_ctx__copy(l, copyContent=True):
	n = []
	for e in l:
		if copyContent:
			n.append(e.copy())
		else:
			n.append(e) #pointing at the same element as in the original list
	return n

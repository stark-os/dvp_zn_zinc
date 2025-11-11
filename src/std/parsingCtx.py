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
	def __init__(sbj, initStr, idx=-1):
		sbj.idx = idx
		sbj.s   = initStr

	def get(sbj):
		return sbj.s[sbj.idx]

	def set(sbj, value):
		sbj.s[sbj.idx] = value

	def forward(sbj, step):
		if (sbj.idx + step) >= len(sbj.s): #could not forward => ret True
			return True
		sbj.idx += step
		return False

	def forwardUntil(sbj, tgtIdx):
		if tgtIdx < sbj.idx: #wrong value given
			return True
		return sbj.forward(tgtIdx - sbj.idx)

	def forwardAlike(sbj, otherIStr):
		return sbj.forwardUntil(otherIStr.idx)

	def inc(sbj):
		return sbj.forward(1)

	def copy(sbj):
		return istr(sbj.s, sbj.idx)

	def reachedEnd(sbj):
		return sbj.idx == len(sbj.s)-1



#constants
PARSING_CTX__INVALID_FIRST_OPENNING        = -1 #these are to be cashted into map[unt_l,unt_l]
PARSING_CTX__INCONSISTENT_INCLUDER_PARSING = -2
PARSING_CTX__PEER_NOT_FOUND                = -3

#external actually but anyway
Term__TAB_LENGTH = 4
Term__CUU1       = "\x1b\x5b\x41"

#parsing ctx object
class ParsingCtx:
	def __init__(sbj, filepath, content, resolveSymlinks=False):
		if resolveSymlinks:
			sbj.filepath = os.path.realpath(filepath)
		else:
			sbj.filepath = os.path.abspath(filepath)
		sbj.dirname    = os.path.dirname(sbj.filepath)
		sbj.filename   = os.path.basename(sbj.filepath)
		sbj.lineNbr    = 1
		sbj.colmNbr    = 0
		sbj.icontent   = istr(content)
		sbj.detectedLF = False

	#copy
	def copy(sbj, filepath=None, content=None):
		if filepath is None:
			filepath = sbj.filepath
		if content is None:
			content  = sbj.icontent.s
		newCtx = ParsingCtx(filepath, content)
		newCtx.icontent.idx = sbj.icontent.idx
		newCtx.lineNbr      = sbj.lineNbr
		newCtx.colmNbr      = sbj.colmNbr
		newCtx.detectedLF   = sbj.detectedLF
		return newCtx

	#print: temporarily made like this
	def toStr(sbj):
		return sbj.filepath + ":" + str(sbj.lineNbr) + ":" + str(sbj.colmNbr)



	#regular parsing
	def get(sbj):
		return sbj.icontent.get()

	def set(sbj, value):
		sbj.icontent.set(value)

	def inc(sbj):
		if sbj.icontent.inc(): #can't go further => can't go further
			return True

		#last character was a line feed => update line indicators
		if sbj.detectedLF:
			sbj.detectedLF = False
			sbj.lineNbr   += 1
			sbj.colmNbr    = 0

		#LF behavior
		if sbj.icontent.get() == '\n':
			sbj.detectedLF = True

		#regular behavior
		sbj.colmNbr += 1
		return False

	def forward(sbj, step):
		for s in range(step):
			if sbj.inc():
				return True
		return False

	def forwardUntil(sbj, tgtIdx):
		return sbj.icontent.forwardUntil(tgtIdx)

	def forwardAlike(sbj, otherCtx):
		return sbj.icontent.forwardAlike(otherCtx.icontent)

	def reachedEnd(sbj):
		return sbj.icontent.reachedEnd()

	def reset(sbj, newText=None):
		sbj.lineNbr    = 1
		sbj.colmNbr    = 0
		sbj.detectedLF = False
		if newText is not None:
			sbj.icontent.s   = newText
			sbj.icontent.idx = -1



	#output
	def lineIndicator(sbj):
		content = sbj.icontent.s

		#set beginning & end of line
		if sbj.icontent.idx == -1: #invalid value (istr starting index)
			begIdx = 0
			endIdx = 0
		else:
			begIdx = sbj.icontent.idx - (sbj.colmNbr-1)
			endIdx = sbj.icontent.idx

		#that mean we are in the first line (cannot subtract colmNbr)
		if begIdx > endIdx:
			begIdx = 0

		#read to get real end of line
		while endIdx < len(content):
			if content[endIdx] == '\n':
				break
			endIdx += 1

		#print full line
		rawConcernedLine = str_sub(content, begIdx, endIdx)
		concernedLine    = str_expandTabs(rawConcernedLine, Term__TAB_LENGTH)

		#prepare position indicator
		positionIdx       = (Term__TAB_LENGTH-1) * rawConcernedLine.count('\t') + sbj.colmNbr - 1
		positionIndicator = ""
		for i in range(positionIdx):
			positionIndicator += '-'
		positionIndicator += '^'

		#print position indicator
		return concernedLine + positionIndicator



	#includers
	def getPairsUntilCorrespondingPeer(sbj, allowedPairs={'(':')', '[':']', '{':'}', '<':'>'}):

		#use local copy of context for precise error indication without affecting the original one
		localCtx = sbj.copy()
		c        = localCtx.get()
		if c in allowedPairs.keys():
			target = allowedPairs[c]

		#current position is not at a valid openning target
		else:
			return PARSING_CTX__INVALID_FIRST_OPENNING

		#prepare main pair (that can contain some other subPairs)
		resultPairs = {} #map[unt_l,unt_l]
		initialIdx  = sbj.icontent.idx

		#read rest of the code taking into account every subPair
		subOpenings = [] #lst[chr]
		subIdxes    = [] #lst[unt_l]
		while not localCtx.inc():
			c = localCtx.get()

			#openning subPair
			if c in allowedPairs.keys():
				subOpenings.append(c)
				subIdxes.append(localCtx.icontent.idx)

			#closing subPair
			elif c in allowedPairs.values():

				#no subzone remaining => looking for the targetted peer
				if lst_isEmpty(subOpenings):

					#found it
					if c == target:
						resultPairs[initialIdx] = localCtx.icontent.idx #add main pair
						return resultPairs

					#inconsistency 1: closing too soon
					print("getPairsUntilCorrespondingPeer: Closing pair with '" + c + "' but expected '" + target + "' (at " + localCtx.toStr() + ").")
					return PARSING_CTX__INCONSISTENT_INCLUDER_PARSING

				#closing latest subPair
				latestOpening = lst_pop(subOpenings)
				latestIdx     = lst_pop(subIdxes)
				if c == allowedPairs[latestOpening]:
					resultPairs[latestIdx] = localCtx.icontent.idx
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

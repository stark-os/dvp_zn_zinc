#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os

#stack
from std.stack import *






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



#parsing ctx object
class ParsingCtx:
	def __init__(self, filepath, content):
		self.filepath   = os.path.realpath(filepath)
		self.dirname    = os.path.dirname(self.filepath)
		self.filename   = os.path.basename(self.filepath)
		self.lineNbr    = 1
		self.columnNbr  = 0
		self.icontent   = istr(content)
		self.detectedLF = False

	#copy
	def copy(self):
		newCtx = ParsingCtx(self.filepath[:], self.icontent.s[:])
		newCtx.icontent.index = self.icontent.index
		newCtx.lineNbr        = self.lineNbr
		newCtx.columnNbr      = self.columnNbr
		newCtx.detectedLF     = self.detectedLF
		return newCtx



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
			self.detectedLF  = False
			self.lineNbr    += 1
			self.columnNbr   = 0

		#LF behavior
		if self.icontent.get() == '\n':
			self.detectedLF = True

		#regular behavior
		self.columnNbr += 1
		return False

	def forward(self, step):
		for s in range(step):
			if self.inc():
				return True
		return False

	def reset(self, newText=None):
		self.lineNbr    = 1
		self.columnNbr  = 0
		self.detectedLF = False
		if newText is not None:
			self.icontent.s     = newText
			self.icontent.index = -1



	#includers
	def getCorrespondingPeerIndex(self,
		peers={
			'(':')',
			'[':']',
			'{':'}',
			'<':'>'
		}
	):

		#use a local copy of context to allow precise indication in errors without affecting the original
		localCtx = self.copy()
		c = localCtx.get()
		if c in peers.keys():
			target = peers[c]
		else:
			return -1 #current position is not at a valid openning target

		#read rest of the code taking into account every oppening subzone
		subZones = Stack()
		while not localCtx.inc():
			c = localCtx.get()

			#oppenning subzone
			if c in peers.keys():
				subZones.push(c)

			#closing subzone
			elif c in peers.values():

				#no subzone remaining => looking for the targetted peer
				if subZones.isEmpty():
					if c == target:
						return localCtx.icontent.index #found it

					#inconsistency 1: closing too soon
					print("getCorrespondingPeerIndex: Closing pair with '" + c + "' but expected '" + target + "' (at " + localCtx.filepath + ":" + str(localCtx.lineNbr) + ":" + str(localCtx.columnNbr) + ").")
					return -2 #inconsistent includer peering

				#closing latest subzone
				subtarget = peers[subZones.pop()]
				if c == subtarget:
					continue

				#inconsistency 2: unexpected peer
				print("getCorrespondingPeerIndex: Closing pair with '" + c + "' but expected '" + subtarget + "' (at " + localCtx.filepath + ":" + str(localCtx.lineNbr) + ":" + str(localCtx.columnNbr) + ").")
				return -2

		#peer not found
		return -3

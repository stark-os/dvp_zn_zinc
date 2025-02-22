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
		self.filepath   = filepath
		self.dirname    = os.path.dirname(filepath)
		self.filename   = os.path.basename(filepath)
		self.lineNbr    = 1
		self.columnNbr  = 1
		self.icontent   = istr(content)
		self.detectedLF = False



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
		self.columnNbr  = 1
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
		c = self.icontent.get()
		if c in peers.keys():
			target = peers[c]
		else:
			return -1 #current position is not at a valid openning target

		#read rest of the code taking into account every oppening subzone
		subZones = Stack()
		icontent = self.icontent.copy() #use copy not to affect current context
		while not icontent.inc():
			c = icontent.get()

			#oppenning subzone
			if c in peers.keys():
				subZones.push(c)

			#closing subzone
			elif c in peers.values():

				#no subzone remaining => looking for the targetted peer
				if subZones.isEmpty():
					if c == target:
						return icontent.index #found it
					return -2                 #inconsistent includer peering

				#closing latest subzone
				elif c == peers[subZones.pop()]:
					continue

				#inconsistent includer peering
				return -2

		#peer not found
		return -3

#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os






# -------- TYPE DEF --------

#istr
class istr:
	def __init__(self, initStr):
		self.index = -1
		self.s     = initStr #[:] #<<<<<<<<<<<<<<<<<<< DO NOT USE A COPY HERE

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

#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.stack      import *
from std.io         import *
from std.parsingCtx import *

#charsets
import string






# -------- CONSTANTS --------

#precompiler
PCPL_VAR_NAME_CHARSET = string.ascii_letters + string.digits + '_'

#general syntax
BLANKS           = (" ", "\t")
VAR_NAME_CHARSET = PCPL_VAR_NAME_CHARSET






# -------- TYPE DEF --------

#precompiler data
class PcplDat:
	def __init__(self, configs, items):
		self.dataResult = {}
		self.items      = items

		#format just a tiny bit pcpl config
		self.configs = {}
		for c in configs.keys():
			v = configs[c]
			if v == "ON":
				self.configs[c] = True
			elif v == "OFF":
				self.configs[c] = False
			else:
				raise ValueError("Invalid value \"" + v + "\" given to precompiler configuration \"" + c + "\".")



#compiler data
class CplDat:
	def __init__(self, options):
		self.options    = options
		self.textResult = ""



#z code context
class ZCtx:
	def __init__(self,
		filepath, LLI,
		pcpl_cfg, pcpl_itm,
		cpl_opt,  debugMode
	):
		self.LLI       = {}
		self.debugMode = debugMode

		#every imported context & the current one
		initialCtx        = ParsingCtx(filepath, readFile(filepath))
		self.ctx          = initialCtx
		self.importedCtxs = Stack()
		self.importedCtxs.push(initialCtx)

		#syntax
		self.scope    = Stack()
		self.includer = Stack()

		#data
		self.zcs  = []
		self.pcpl = PcplDat(pcpl_cfg, pcpl_itm)
		self.cpl  = CplDat(cpl_opt)



	#parsing shortcut relays
	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def forward(self, step):
		return self.ctx.forward(step)



	#file contexts
	def openNewSubCtx(self, filepath):
		newCtx   = ParsingCtx(filepath, readFile(filepath))
		self.ctx = newCtx
		self.importedCtxs.append(newCtx)

	def closeCurrentCtx(self): #return True if no more context remains
		self.importedCtxs.pop()
		if self.importedCtxs.isEmpty():
			return True
		self.ctx = self.importedCtxs.last()
		return False



	#output
	def debug(self, msg):
		print("[ DEBUG ] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))

	def warning(self, msg):
		print("[WARNING] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))

	def error(self, msg):
		print("[ ERROR ] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))
		exit(1)

	def internal(self, msg):
		print("[INT ERR] " + msg)
		for ctx in self.importedCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.filepath + ':' + str(ctx.lineNbr) + ':' + str(ctx.columnNbr))
		exit(2)

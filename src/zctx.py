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
VAR_NAME_CHARSET = PCPL_VAR_NAME_CHARSET






# -------- TYPE DEF --------

#precompiler data
class PcplDat:
	def __init__(self, configs, items):
		self.configs    = configs
		self.items      = items
		self.dataResult = {}



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
		self.ctx       = ParsingCtx(filepath, readFile(filepath))
		self.scope     = Stack()
		self.includer  = Stack()
		self.zcs       = []
		self.pcpl      = PcplDat(pcpl_cfg, pcpl_itm)
		self.cpl       = CplDat(cpl_opt)
		self.LLI       = {}
		self.debugMode = debugMode

	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def debug(self, msg):
		print("[ DEBUG ] " + msg)
		print("    At " + self.ctx.filepath + ':' + str(self.ctx.lineNbr) + ':' + str(self.ctx.columnNbr))

	def warning(self, msg):
		print("[WARNING] " + msg)
		print("    At " + self.ctx.filepath + ':' + str(self.ctx.lineNbr) + ':' + str(self.ctx.columnNbr))

	def error(self, msg):
		print("[ ERROR ] " + msg)
		print("    At " + self.ctx.filepath + ':' + str(self.ctx.lineNbr) + ':' + str(self.ctx.columnNbr))
		exit(1)

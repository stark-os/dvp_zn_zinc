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






# -------- PRECOMPILATION --------

#precompiler data
class pcplDat:
	def __init__(self, configs, items):
		self.items      = items
		self.configs    = configs
		self.ZCIs       = None #lst[^Parsing.ctx]

#format configs
def pcplDat_new(configs, items):
	formatted_configs = {}
	for c in configs.keys():
		v = configs[c]
		if v == "ON":
			formatted_configs[c] = True
		elif v == "OFF":
			formatted_configs[c] = False
		else:
			raise ValueError("Invalid value \"" + v + "\" given to precompiler configuration \"" + c + "\".")
	return pcplDat(formatted_configs, items)

#includers
INCLUDERS = { '(':')', '[':']', '{':'}' }






# -------- COMPILATION --------

#program structure
class program:
	def __init__(self):
		self.globalData = []
		self.types      = []
		self.functions  = []

#compiler data
class cplDat:
	def __init__(self, options):
		self.options    = options
		self.dataResult = program()
		self.textResult = ""






# -------- GENERAL --------

#z code context
class zctx:
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
		self.imported     = Stack() #history of every filename imported
		self.subCtxs      = Stack() #subcontexts currently in use
		self.subCtxs.push(initialCtx)

		#syntax
		self.scope    = Stack()
		self.includer = Stack()

		#data
		self.zcs  = []
		self.pcpl = pcplDat_new(pcpl_cfg, pcpl_itm)
		self.cpl  = cplDat(cpl_opt)



	#parsing shortcut relays
	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def forward(self, step):
		return self.ctx.forward(step)



	#output
	def debug(self, msg):
		print("[ DEBUG ] " + msg)
		for ctx in self.subCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.toStr())

	def warning(self, msg):
		print("[WARNING] " + msg)
		for ctx in self.subCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.toStr())

	def error(self, msg):
		print("[ ERROR ] " + msg)
		for ctx in self.subCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.toStr())
		exit(1)

	def internal(self, msg):
		print("[INT ERR] " + msg)
		for ctx in self.subCtxs.data: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< could have avoided .data in Z using indexing functions
			print("    At " + ctx.toStr())
		exit(2)



	#file contexts return true if successfully openned (false means : file already processed => ignoring it)
	def openNewSubCtx(self, filepath):
		if not filepath.endswith(".z"):
			filepath += ".z"

		#resolve relativeness of given filepath regarding current context location
		if not filepath.startswith('/'):
			filepath = self.ctx.dirname + '/' + filepath

		#open new subcontext
		try:
			newCtx   = ParsingCtx(filepath, readFile(filepath))
		except FileNotFoundError:
			self.error("File " + filepath + " not found.")
		except IsADirectoryError:
			self.error("Element " + filepath + " is a directory (expected file).")

		#check already openned
		realNewPath = os.path.realpath(newCtx.filepath)
		for c in self.imported.data:
			if realNewPath == c:
				return False

		#not already openned => add it to importations
		self.ctx = newCtx
		self.subCtxs.push(newCtx)
		self.imported.push(realNewPath)
		return True

	def closeCurrentCtx(self): #return True if no more context remains
		self.subCtxs.pop()
		if self.subCtxs.isEmpty():
			return True
		self.ctx = self.subCtxs.last()
		return False

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output1.py

	#output
	def internal(self, msg, printSubCtxs=True, printLine=True):
		print("[INT ERR] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if self.ctx is None:
				self.internal("No context to internal-output line from.", printSubCtxs=False, printLine=False)
			self.ctx.printLineIndicator()
		import traceback #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< can be useful
		traceback.print_stack()
		exit(2)

	def error(self, msg, printSubCtxs=True, printLine=True):
		print("[ ERROR ] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if self.ctx is None:
				self.internal("No context to error-output line from.", printSubCtxs=False, printLine=False)
			self.ctx.printLineIndicator()
		exit(1)

	def warning(self, msg, printSubCtxs=True, printLine=True):
		print("[WARNING] " + msg)
		if printSubCtxs:
			for ctx in self.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if self.ctx is None:
				self.internal("No context to warning-output line from.", printSubCtxs=False, printLine=False)
			self.ctx.printLineIndicator()

	def debug(self, msg, printSubCtxs=False, printLine=False):
		if self.debugMode:
			print("[ DEBUG ] " + msg)
			if printSubCtxs:
				for ctx in self.subCtxs:
					print("    At " + ctx.toStr())
			if printLine:
				if self.ctx is None:
					self.internal("No context to debug-output line from.", printSubCtxs=False, printLine=False)
				self.ctx.printLineIndicator()

	def deepDebug(self, msg, printSubCtxs=False, printLine=False):
		if self.deepDebugMode:
			print("[D-DEBUG] " + msg)
			if printSubCtxs:
				for ctx in self.subCtxs:
					print("    At " + ctx.toStr())
			if printLine:
				if self.ctx is None:
					self.internal("No context to deep-debug-output line from.", printSubCtxs=False, printLine=False)
				self.ctx.printLineIndicator()

	def deepDebugPause(self):
		if self.deepDebugMode and deepDebug_stepByStep:
			print("~ ~ ~ ~ Press ENTER to continue ~ ~ ~ ~", end="")
			input()
			print(Term__CUU1 + "                                       \r", end="")



#imp parsing






# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output1.py

	#output
	def internal(sbj, msg, printSubCtxs=True, printLine=True):
		print("[INT ERR] " + msg)
		if printSubCtxs:
			for ctx in sbj.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if sbj.ctx is None:
				sbj.internal("No context to internal-output line from.", printSubCtxs=False, printLine=False)
			sbj.ctx.printLineIndicator()
		import traceback #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< can be useful
		traceback.print_stack()
		exit(2)

	def error(sbj, msg, printSubCtxs=True, printLine=True):
		print("[ ERROR ] " + msg)
		if printSubCtxs:
			for ctx in sbj.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if sbj.ctx is None:
				sbj.internal("No context to error-output line from.", printSubCtxs=False, printLine=False)
			sbj.ctx.printLineIndicator()
		exit(1)

	def warning(sbj, msg, printSubCtxs=True, printLine=True):
		print("[WARNING] " + msg)
		if printSubCtxs:
			for ctx in sbj.subCtxs:
				print("    At " + ctx.toStr())
		if printLine:
			if sbj.ctx is None:
				sbj.internal("No context to warning-output line from.", printSubCtxs=False, printLine=False)
			sbj.ctx.printLineIndicator()

	def debug(sbj, msg, printSubCtxs=False, printLine=False):
		if sbj.debugMode:
			print("[ DEBUG ] " + msg)
			if printSubCtxs:
				for ctx in sbj.subCtxs:
					print("    At " + ctx.toStr())
			if printLine:
				if sbj.ctx is None:
					sbj.internal("No context to debug-output line from.", printSubCtxs=False, printLine=False)
				sbj.ctx.printLineIndicator()

	def deepDebug(sbj, msg, printSubCtxs=False, printLine=False):
		if sbj.deepDebugMode:
			print("[D-DEBUG] " + msg)
			if printSubCtxs:
				for ctx in sbj.subCtxs:
					print("    At " + ctx.toStr())
			if printLine:
				if sbj.ctx is None:
					sbj.internal("No context to deep-debug-output line from.", printSubCtxs=False, printLine=False)
				sbj.ctx.printLineIndicator()

	def debugSepLine(sbj):
		if sbj.debugMode:
			Term__drawSepLine()

	def deepDebugPause(sbj):
		if sbj.deepDebugMode and deepDebug_stepByStep:
			print("~ ~ ~ ~ Press ENTER to continue ~ ~ ~ ~", end="")
			input()
			print(Term__CUU1 + "                                       \r", end="")
			Term__drawSepLine()



#imp parsing






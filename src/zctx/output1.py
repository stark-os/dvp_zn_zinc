# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output1.py

	#output
	def int(sbj, msg, prtSubCtxs=True, prtLine=True):
		print("[INT ERR] " + msg)
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				print("    At " + ctx.toStr())
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to internal-output line from.", prtSubCtxs=False, prtLine=False)
			sbj.ctx.prtLineIndicator()
		import traceback #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< can be useful
		traceback.print_stack()
		exit(2)

	def err(sbj, msg, prtSubCtxs=True, prtLine=True):
		print("[ ERROR ] " + msg)
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				print("    At " + ctx.toStr())
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to error-output line from.", prtSubCtxs=False, prtLine=False)
			sbj.ctx.prtLineIndicator()
		exit(1)

	def wrn(sbj, msg, prtSubCtxs=True, prtLine=True):
		print("[WARNING] " + msg)
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				print("    At " + ctx.toStr())
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to warning-output line from.", prtSubCtxs=False, prtLine=False)
			sbj.ctx.prtLineIndicator()

	def dbg(sbj, msg, prtSubCtxs=False, prtLine=False):
		if sbj.dbgMode[sbj.step]:
			print("[ DEBUG ] " + msg)
			if prtSubCtxs:
				for ctx in sbj.subCtxs:
					print("    At " + ctx.toStr())
			if prtLine:
				if sbj.ctx is None:
					sbj.int("No context to debug-output line from.", prtSubCtxs=False, prtLine=False)
				sbj.ctx.prtLineIndicator()

	def deepDbg(sbj, msg, prtSubCtxs=False, prtLine=False):
		if sbj.deepDbgMode[sbj.step]:
			print("[D-DEBUG] " + msg)
			if prtSubCtxs:
				for ctx in sbj.subCtxs:
					print("    At " + ctx.toStr())
			if prtLine:
				if sbj.ctx is None:
					sbj.int("No context to deep-debug-output line from.", prtSubCtxs=False, prtLine=False)
				sbj.ctx.prtLineIndicator()

	def dbgSepLine(sbj):
		if sbj.dbgMode[sbj.step]:
			Term__drawSepLine()

	def deepDbgPause(sbj):
		if sbj.deepDbgMode[sbj.step] and sbj.stepByStep:
			print("~ ~ ~ ~ Press ENTER to continue ~ ~ ~ ~", end="")
			input()
			print(Term__CUU1 + "                                       \r", end="")
			Term__drawSepLine()



#imp parsing






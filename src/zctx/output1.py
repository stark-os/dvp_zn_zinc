# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output1.py

	#output
	def int(sbj, msg, prtSubCtxs=True, prtLine=True):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "    At " + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to internal-output line from.", prtSubCtxs=False, prtLine=False)
			out += sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_int(out)

		#exit
		import traceback #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< can be useful
		traceback.print_stack()
		exit(2)



	def err(sbj, msg, prtSubCtxs=True, prtLine=True, err=1):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "    At " + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to error-output line from.", prtSubCtxs=False, prtLine=False)
			out += sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_err(out)

		#additional dbg info IN STDOUT !
		if sbj.dbgMode[sbj.step]:
			log_dbg("Types ID table: " + sbj.listTypeNames())

		#exit
		exit(err)



	def wrn(sbj, msg, prtSubCtxs=True, prtLine=True):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "    At " + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to warning-output line from.", prtSubCtxs=False, prtLine=False)
			out += sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_wrn(out)



	def dbg(sbj, msg, prtSubCtxs=False, prtLine=False):
		out = ""
		if sbj.dbgMode[sbj.step]:

			#additional ver spacing
			if prtSubCtxs or prtLine:
				out += "\n\n\n"

			#subCtxs
			if prtSubCtxs:
				for ctx in sbj.subCtxs:
					out += "    At " + ctx.toStr() + '\n'

			#code line
			if prtLine:
				if sbj.ctx is None:
					sbj.int("No context to debug-output line from.", prtSubCtxs=False, prtLine=False)
				out += sbj.ctx.lineIndicator() + '\n'

			#msg
			out += msg
			log_dbg(out)



	def deepDbg(sbj, msg, prtSubCtxs=False, prtLine=False):
		out = ""
		if sbj.deepDbgMode[sbj.step]:

			#additional ver spacing
			if prtSubCtxs or prtLine:
				out += "\n\n\n"

			#subCtxs
			if prtSubCtxs:
				for ctx in sbj.subCtxs:
					out += "    At " + ctx.toStr() + '\n'

			#code line
			if prtLine:
				if sbj.ctx is None:
					sbj.int("No context to deep-debug-output line from.", prtSubCtxs=False, prtLine=False)
				out += sbj.ctx.lineIndicator() + '\n'

			#log
			out += msg
			log_deepDbg(out)



	def dbgSepLine(sbj):
		if sbj.dbgMode[sbj.step]:
			Term__drawSepLine()



	def deepDbgPause(sbj):
		if sbj.deepDbgMode[sbj.step] and sbj.stepByStep:
			log_deepDbg("~ ~ ~ ~ Press ENTER to continue ~ ~ ~ ~", end="")
			input()
			log_deepDbg(Term__CUU1 + "                                       \r", end="")
			Term__drawSepLine()



#imp parsing



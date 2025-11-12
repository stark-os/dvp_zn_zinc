# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output1.py

	#output
	def int(sbj, msg, prtSubCtxs=True, prtLine=True):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to internal-output line from.", prtSubCtxs=False, prtLine=False)
			out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_intLF(out)

		#exit
		import traceback #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< can be useful
		traceback.print_stack()
		exit(2)



	def err(sbj, msg, prtSubCtxs=True, prtLine=True, err=1):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to error-output line from.", prtSubCtxs=False, prtLine=False)
			out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_errLF(out)

		#exit
		if err != 0:
			if sbj.dbgMode[sbj.step]: #additional dbg info IN STDOUT !
				log_dbgLF("Types ID table: " + sbj.listTypeNames())
			exit(err)



	def wrn(sbj, msg, prtSubCtxs=True, prtLine=True):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is None:
				sbj.int("No context to warning-output line from.", prtSubCtxs=False, prtLine=False)
			out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_wrnLF(out)



	def dbg(sbj, msg, prtSubCtxs=False, prtLine=False):
		out = ""
		if sbj.dbgMode[sbj.step]:

			#additional ver spacing
			if prtSubCtxs or prtLine:
				out += "\n\n\n"

			#subCtxs
			if prtSubCtxs:
				for ctx in sbj.subCtxs:
					out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

			#code line
			if prtLine:
				if sbj.ctx is None:
					sbj.int("No context to debug-output line from.", prtSubCtxs=False, prtLine=False)
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

			#msg
			out += msg
			log_dbgLF(out)



	def deepDbg(sbj, msg, prtSubCtxs=False, prtLine=False):
		out = ""
		if sbj.deepDbgMode[sbj.step]:

			#additional ver spacing
			if prtSubCtxs or prtLine:
				out += "\n\n\n"

			#subCtxs
			if prtSubCtxs:
				for ctx in sbj.subCtxs:
					out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

			#code line
			if prtLine:
				if sbj.ctx is None:
					sbj.int("No context to deep-debug-output line from.", prtSubCtxs=False, prtLine=False)
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

			#log
			out += msg
			log_deepDbgLF(out)



	def dbgSepLine(sbj):
		if sbj.dbgMode[sbj.step]:
			Term__drawSepLine()



	def deepDbgPause(sbj):
		if sbj.deepDbgMode[sbj.step] and sbj.stepByStep:
			log_deepDbg("~ ~ ~ ~ Press ENTER to continue ~ ~ ~ ~")
			input()
			log_deepDbg(Term__CUU1 + "                                       \r")
			Term__drawSepLine()



#imp parsing



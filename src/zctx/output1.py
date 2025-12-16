# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output1.py

	#log lvl
	def updateLogLvl(sbj, step):
		sbj.step   = step
		log_lvl[0] = sbj.log_lvls[step]



	#output
	def int(sbj, msg, prtSubCtxs=True, prtLine=True):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is not None:
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_intLF(out)
		log_dbg0LF("Types ID table: " + sbj.listTypeNames())

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
			if sbj.ctx is not None:
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_errLF(out)

		#exit
		if err != 0:
			log_dbg0LF("Types ID table: " + sbj.listTypeNames())
			exit(err)



	def wrn(sbj, msg, prtSubCtxs=True, prtLine=True):
		out = ""

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is not None:
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_wrnLF(out)



	def dbg0(sbj, msg, prtSubCtxs=False, prtLine=False):
		out = ""

		#additional ver spacing
		if prtSubCtxs or prtLine:
			out += "\n"

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is not None:
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#msg
		out += msg
		log_dbg0LF(out)



	def dbg1(sbj, msg, prtSubCtxs=False, prtLine=False):
		out = ""

		#additional ver spacing
		if prtSubCtxs or prtLine:
			out += "\n"

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is not None:
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#log
		out += msg
		log_dbg1LF(out)



	def dbg2(sbj, msg, prtSubCtxs=False, prtLine=False):
		out = ""

		#additional ver spacing
		if prtSubCtxs or prtLine:
			out += "\n"

		#subCtxs
		if prtSubCtxs:
			for ctx in sbj.subCtxs:
				out += "At " + LOG__COLOR_NEUTRAL + ctx.toStr() + '\n'

		#code line
		if prtLine:
			if sbj.ctx is not None:
				out += LOG__COLOR_TEXT + sbj.ctx.lineIndicator() + '\n'

		#log
		out += msg
		log_dbg2LF(out)



	def dbgSepLine(sbj):
		if log_lvl[0] >= LOG__LVL_DBG0:
			Term__drawSepLine()



	def dbgPause(sbj):
		if log_lvl[0] >= LOG__LVL_DBG0 and sbj.stepByStep:
			log_dbg0("~ ~ ~ ~ Press ENTER to continue ~ ~ ~ ~")
			input()
			log_dbg0(Term__CUU1 + "                                       \r")
			Term__drawSepLine()



#imp parsing



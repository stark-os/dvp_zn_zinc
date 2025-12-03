#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *

#obv
from obv import *






# -------- EXECUTION --------

#main
def c09_rmUnreadLcls(zCtx):
	zCtx.updateLogLvl(STEP.C09)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================= C09 RM UNREAD LCLS : beginning ========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	'''
	#flags
	inGblScp = True
	rmCurOx  = False

	#flexible iter
	l = 0
	while True:
		if l >= len(zCtx.cpl.resObv):
			break

		#try parsing (can be empty line)
		ox = obvParse(zCtx.cpl.resObv[l])
		if ox is not None:

			#skip gbl scp (no optimization for gbl unread datItms, potential ext use in DATA segment, even if cur prg does not read them)
			if inGblScp and ox.ist == "fct":
				inGblScp = False
				zCtx.dbg0("=> Start lcl parsing here  \"" + ox.toStr() + "\".")
			if inGblScp:
				l += 1
				continue
			zCtx.dbg1("Analysing current OBV exe  \"" + ox.toStr() + "\".")



			# IN THE RIGHT CTX

			#cpy ist => can potentially be optimized
			if obvExe_isCpy(ox.ist):
				#stillNeverRead = True

				#read the rest of the code from the nxt ist
				for subL in range(l+1, len(zCtx.cpl.resObv)): #<<<<<<<<<<<<<<<<<<<<<<<<<<<<< in Z, 2nd limit would be len-1 (excluded in python)
					subLine = zCtx.cpl.resObv[subL]
					subOx   = obvParse(subLine)

					#can't go deeper => stop here
					if subOx is None:
						break

					#dat inoffensive ist => just skip it
					if subOx.ist == "rsv":
						continue

					#dat offensive ist => stop here
					if not obvExe_isCpy(subOx.ist):
						#if subOx.ist in ("ivq", "syc") and ox.args[1] in OBV__REGS:
						#	stillNeverRead = False #considering being read if used by a [sys]call
						break

					#at least the same memory location has been used for reading => prev write was potentially useful !
					if subOx.args[0].split('+')[0] == ox.args[1].split('+')[0]:
						#stillNeverRead = False
						break

					#same exact memory location tgted
					if subOx.args[1] == ox.args[1]:
						


					#smaller size => cur write is not be enough for taking over writing
					firstCpySize = obvExe_cpyIst_getSize(zCtx, ox)
					if firstCpySize > obvExe_cpyIst_getSize(zCtx, subOx):
						

					#optimization!
					# Write twice in the same location, the same amount, and it has not been used in between
					# => rm the 1st one
					if stillNeverRead:
						zCtx.dbg0("The cur cpy ist can be rm  \"" + ox.toStr() + "\" because no one read")
						zCtx.dbg0("its dst before its nxt cpy \"" + subOx.toStr() + "\" a bit further away.")
						rmCurOx = True

				#unread lcl <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Hmmm...
				#if stillNeverRead:
				#	...well, don't rm it too fast, this is a bit more complicated...

				#rm cur obv exe
				if rmCurOx:
					rmCurOx = False
					zCtx.cpl.resObv = lst_remove(zCtx.cpl.resObv, l)
					continue #rm cur ox => no need to inc ! "l" is good

		#inc
		l += 1
	'''

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================= C09 RM UNREAD LCLS : end ========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#final msg if everything went OK, still cool to have that info
	zCtx.dbg0("Types ID table: " + zCtx.listTypeNames())

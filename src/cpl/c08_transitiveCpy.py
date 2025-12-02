#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *

#obv
from obv import *






# -------- PARSING TOOLS --------

#extract OBV ist & args from line
def obvParse(rawLine):
	commentIdx = str_findFirstChr(rawLine, '#')
	if commentIdx != -1:
		rawLine = str_sub(rawLine, stop=commentIdx-1)

	#strip
	line        = str_stripBeg(rawLine)
	begBlankLen = len(rawLine) - len(line)
	line        = str_stripEnd(line)

	#parse
	return obvExe(
		line[:3],
		line.split(OBV__SEP)[1:],
		rawLine[:begBlankLen]
	)

#size
def obvExe_cpyIst_getSize(zCtx, ox):
	size = zCtx.smaxSize
	if ox.ist[0] == 'v':
		size = int( len(ox.args[0])/2 )
	elif ox.ist[0] == 'd' and ox.ist[2] == 'd':
		size = str_hex_toS16(ox.args[2])
	return size






# -------- EXECUTION --------

#main
def c08_transitiveCpy(zCtx):
	zCtx.updateLogLvl(STEP.C08)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================= C08 TRANSITIVE CPY : beginning ========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#flexible iter
	l = 0
	while True:
		if l >= len(zCtx.cpl.resObv):
			break

		#try parsing (can be empty line)
		ox = obvParse(zCtx.cpl.resObv[l])
		if ox is not None:
			zCtx.dbg1("Analysing current OBV exe  \"" + ox.toStr() + "\".")

			#transitive cpy requires at least 2 exe, and a datItm/reg as 2nd arg
			if l != len(zCtx.cpl.resObv)-1 and ox.ist in ("v2d","v2r", "d2d","d2r", "r2d","r2r"):
				line2 = zCtx.cpl.resObv[l+1]
				ox2   = obvParse(line2)
				if ox2 is not None:

					#2nd exe must have datItm/reg as 1st arg
					if ox2.ist in ("d2d","d2r", "r2d","r2r"):
						cpySize1 = obvExe_cpyIst_getSize(zCtx, ox)
						cpySize2 = obvExe_cpyIst_getSize(zCtx, ox2)

						#same location, same size => transitivity
						if ox.args[1] == ox2.args[0] and cpySize1 == cpySize2:
							zCtx.dbg0("When analysing cur OBV exe \"" + ox.toStr() + "\",\n=> transitive with nxt one \"" + ox2.toStr() + "\".")

							#transitivity => update obv exe to skip itermediate transiter
							ox.ist     = ox.ist[:2] + ox2.ist[2] #<<<<<<<<<<<<<<<<<<<<<<<<< in Z, "ox.ist[2] = ox2.ist[2]"
							ox.args[1] = ox2.args[1]
							zCtx.dbg0("Cur OBV exe changed into   \"" + ox.toStr() + "\".")

							#apply changes & rm nxt ist
							zCtx.cpl.resObv[l] = ox.toStr()
							zCtx.cpl.resObv    = lst_remove(zCtx.cpl.resObv, l+1)

							#also write in transiter BEFORE to preserve transitivity chain (use ox2 for mem usage opti, but it will be set before "ox")
							ox2 = obvExe(
								ox.ist[0] + '2' + ox2.ist[0],
								[ox.args[0], ox2.args[0]],
								ox.begBlanks
							)
							if ox2.ist == "d2d":
								ox2.args.append(hexOnN(cpySize1, 4))
							lst_insertBefore(zCtx.cpl.resObv, l, ox2.toStr())
							zCtx.dbg0("Also prepended cur OBV exe \"" + ox2.toStr() + "\".")

							#don't go to nxt exe, we can have several transitive copies chained together
							continue

			#no-cpy detected => rm ist
			if ox.ist in ("d2d", "r2r"):
				if ox.args[0] == ox.args[1]:
					zCtx.dbg0("No-move detected => rm it  \"" + ox.toStr() + "\".")
					zCtx.cpl.resObv = lst_remove(zCtx.cpl.resObv, l)

					#rm cur ox => no need to inc ! "l" is good
					continue

		#inc
		l += 1

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================= C08 TRANSITIVE CPY : end ========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#final msg if everything went OK, still cool to have that info
	zCtx.dbg0("Types ID table: " + zCtx.listTypeNames())

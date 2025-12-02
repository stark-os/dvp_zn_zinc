#!/usr/bin/python3



# -------- IMPORTATIONS --------

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< should be already shared from src/main.z, Pythonic
import sys, os
CXD = os.path.dirname(os.path.realpath(sys.argv[0]))

#internal
from zctx import *






# -------- SPECIFIC UNPARSE --------

#value
def unparseVal(zCtx, depth, v):
	zCtx.dbg0("Unparsing VAL " + v.toStr(depth=1))

	#lit int
	if v.vdat.id in (ATM__S8,  ATM__U8):
		zCtx.dbg0("Unparsed VAL (lit 8b).")
		return (OBV__VAL_LIT, hexOnN(v.vdat.dat, 2))
	if v.vdat.id in (ATM__S16, ATM__U16):
		zCtx.dbg0("Unparsed VAL (lit 16b).")
		return (OBV__VAL_LIT, hexOnN(v.vdat.dat, 4))
	if v.vdat.id in (ATM__S32, ATM__U32):
		zCtx.dbg0("Unparsed VAL (lit 32b).")
		return (OBV__VAL_LIT, hexOnN(v.vdat.dat, 8))
	if v.vdat.id in (ATM__S64, ATM__U64):
		zCtx.dbg0("Unparsed VAL (lit 64b).")
		return (OBV__VAL_LIT, hexOnN(v.vdat.dat, 16))

	#datItm
	if v.vdat.id == ATM__DATITM:
		name = '_'*(depth+1) + v.vdat.dat.name
		zCtx.dbg0("Unparsed VAL (datItm).")
		return (OBV__VAL_DATITM, name + "+0000")

	#call
	if v.vdat.id == ATM__CALL:
		unparseCall(zCtx, depth, v.vdat.dat)
		zCtx.dbg0("Unparsed VAL (call).")
		return (OBV__VAL_REG, "r")

	#raw data
	if v.vdat.id == ATM__LST_VAL:
		res = hexOnN(len(v.vdat.dat), zCtx.smaxSize*2)
		for c in v.vdat.dat:
			res += hexOnN(c.vdat.dat, 2)
		zCtx.dbg0("Unparsed VAL (lst[val]).")
		return (OBV__VAL_LIT, res)

	#ffa
	if v.vdat.id == ATM__FFA:
		obvValType, txt = unparseVal(zCtx, depth, v.vdat.dat.value)
		if obvValType != OBV__VAL_DATITM:
			zCtx.int("Still have FFA value on a non-datItm val " + v.vdat.dat.value.toStr(), prtSubCtxs=False, prtLine=False)

		#remove prev 0 offset, to set ours
		plusIdx     = str_findFirstChr(txt, '+')
		nameAndPlus = str_sub(txt, stop=plusIdx)

		#int err
		prevOffset = str_sub(txt, start=plusIdx+1)
		if prevOffset != "0000":
			zCtx.int("Got non-zero offset in datItm used in FFA => SHOULDN'T BE!")

		#res
		return (OBV__VAL_DATITM, nameAndPlus + hexOnN(v.vdat.dat.offset, 4))

	#unknown
	zCtx.int("Unknown ID " + str(v.vdat.id) + " in value " + v.toStr(), prtSubCtxs=False, prtLine=False)
	return (OBV__VAL__UNKNOWN, "") #unreachable



#datItm
def unparseDclDat(zCtx, depth, di):
	zCtx.dbg0("Unparsing DCL DAT.")
	d   = RES__OUTPUT_TAB * depth
	res = [""]

	#type size
	sizeTxt = hexOnN(zCtx.getTypeInstanceFromID(di.Type).dcnCommon.size, 4)

	#pfx name
	name = '_'*(depth+1) + di.name

	#rsv
	res[0] = d + "rsv" + OBV__SEP + name + OBV__SEP + sizeTxt

	#initVal
	if di.inited:
		res.append(d)
		obvValType, txt = unparseVal(zCtx, depth, di.initVal)
		if obvValType == OBV__VAL_LIT:
			res[1] += "v2d" + OBV__SEP + name + OBV__SEP + txt
		elif obvValType == OBV__VAL_DATITM:
			res[1] += "d2d" + OBV__SEP + name + OBV__SEP + txt + sizeTxt
		elif obvValType == OBV__VAL_REG:
			res[1] += "r2d" + OBV__SEP + name + OBV__SEP + txt

	#output
	zCtx.cpl.resObv += res
	zCtx.dbg0("Unparsed DCL DAT.")



#asg
def unparseAsg(zCtx, depth, a):
	zCtx.dbg0("Unparsing ASG " + a.toStr(depth=1))
	d   = RES__OUTPUT_TAB * depth
	res = d[:]

	#src
	srcObvType, srcValTxt = unparseVal(zCtx, depth, a.src)

	#dst
	dstObvType, dstValTxt = unparseVal(zCtx, depth, a.dst)
	dstSizeTxt            = hexOnN(zCtx.getTypeInstanceFromID(a.dst.Type).dcnCommon.size, 4)

	#invalid dst
	if dstObvType == OBV__VAL_LIT:
		zCtx.int("Got assignment into a literal value (makes no sens) " + a.toStr())

	#write: from lit
	if srcObvType == OBV__VAL_LIT:
		if dstObvType == OBV__VAL_DATITM:
			res += "v2d" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt
		if dstObvType == OBV__VAL_REG:
			res += "v2r" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt

	#write: from
	elif srcObvType == OBV__VAL_DATITM:
		if dstObvType == OBV__VAL_DATITM:
			res += "d2d" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt + OBV__SEP + dstSizeTxt
		if dstObvType == OBV__VAL_REG:
			res += "d2r" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt

	#write: from register
	else:
		if dstObvType == OBV__VAL_DATITM:
			res += "r2d" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt
		if dstObvType == OBV__VAL_REG:
			res += "r2r" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt

	#output
	zCtx.cpl.resObv.append(res)
	zCtx.dbg0("Unparsed ASG.")



#stm if
def unparseStmIf(zCtx, i, depth, begEnd=True):
	'''if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"if(cond){scp}else if(cond){scp}else{scp}"
	zCtx.dbg0("Unparsing IF " + i.toStr(depth=1))
	d = RES__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#conditional blocks
	zCtx.cpl.resC += "if("
	unparseVal(zCtx, i.cond, depth)
	zCtx.cpl.resC += "){\n"
	unparseScope(zCtx, i.ifScope, depth)
	if i.elsScope is not None:
		zCtx.cpl.resC += d + "}else{\n"
		unparseScope(zCtx, i.elsScope, depth)
	zCtx.cpl.resC += d + "}\n"
	'''
	zCtx.dbg0("Unparsed IF.")



#whi
def unparseStmWhi(zCtx, w, depth, begEnd=True):
	'''if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"while(cond){scp}"
	zCtx.dbg0("Unparsing WHI " + w.toStr(depth=1))
	d = RES__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d
	zCtx.cpl.resC += "while("

	#iterCond
	unparseVal(zCtx, w.iterCond, depth)
	zCtx.cpl.resC += "){\n"

	#scope
	unparseScope(zCtx, w.scope, depth=depth)
	zCtx.cpl.resC += d + "}\n"
	'''
	zCtx.dbg0("Unparsed WHI.")



#swi
def unparseStmSwi(zCtx, s, depth, begEnd=True):
	'''if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"switch(){case c1val:{scp} c2val:{scp} def:{}}"
	zCtx.dbg0("Unparsing SWI " + s.toStr(depth=1))
	d   = RES__OUTPUT_TAB * depth
	dp1 = d + RES__OUTPUT_TAB

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d
	zCtx.cpl.resC += "switch("

	#tgt
	unparseVal(zCtx, s.tgt, depth)
	zCtx.cpl.resC += "){\n"

	#for each case
	c = 0
	while c < len(s.cases):
		zCtx.cpl.resC += dp1 + "case "
		unparseVal(zCtx, s.cases[c], depth)
		zCtx.cpl.resC += ": {\n"
		unparseScope(zCtx, s.scopes[c], depth=depth)
		zCtx.cpl.resC += dp1 + "}\n"
		c += 1

	#def block
	if len(s.scopes) > len(s.cases):
		zCtx.cpl.resC += dp1 + "default: {\n"
		unparseScope(zCtx, s.scopes[c], depth=depth)
		zCtx.cpl.resC += dp1 + "}\n"
	zCtx.cpl.resC = d + "}\n"
	'''
	zCtx.dbg0("Unparsed SWI.")



#jmp
def unparseJmp(zCtx, depth, j):
	zCtx.dbg0("Unparsing JMP " + j.toStr(depth=1))
	d   = RES__OUTPUT_TAB * depth
	res = [d[:]]

	#brk
	if j.kind == JMP__BRK:
		res[0] += "BREAK\n"

	#ctn
	if j.kind == JMP__CTN:
		res[0] += "CONTINUE\n"

	#ret
	if j.kind == JMP__RET:
		if j.retVal is not None:
			obvValType, txt = unparseVal(zCtx, depth, j.retVal)
			if obvValType == OBV__VAL_LIT:
				res[0] += "v2r"
			if obvValType == OBV__VAL_DATITM:
				res[0] += "d2r"
			else:
				res[0] += "r2r"
			res[0] += OBV__SEP + txt + OBV__SEP + 'r'
		res.append(d + "bck")

	#output
	zCtx.cpl.resObv += res
	zCtx.dbg0("Unparsed JMP.")



#call
def unparseCall(zCtx, depth, c):
	zCtx.dbg0("Unparsing CALL " + c.toStr(depth=1))
	d   = RES__OUTPUT_TAB * depth
	res = [d[:]]

	#params
	p = 0
	while p < len(c.paramVals):
		res.append(d[:])

		#set pX reg
		obvValType, txt = unparseVal(zCtx, depth, c.paramVals[p])
		if obvValType == OBV__VAL_LIT:
			res[p] += "v2r"
		elif obvValType == OBV__VAL_DATITM:
			res[p] += "d2r"
		else:
			res[p] += "r2r"
		res[p] += OBV__SEP + txt + OBV__SEP + 'p' + str(p+1)

		#inc
		p += 1

	#ivq
	res[p] += "ivq" + OBV__SEP + c.name

	#output
	zCtx.cpl.resObv += res
	zCtx.dbg0("Unparsed CALL.")






# -------- MAIN UNPARSE --------

#exe
def unparseExe(zCtx, depth, x):
	if x.id == ATM__ASG:
		unparseAsg(zCtx, depth, x.dat)
	elif x.id == ATM__STM_IF:
		unparseStmIf(zCtx, depth, x.dat)
	elif x.id == ATM__STM_WHI:
		unparseStmWhi(zCtx, depth, x.dat)
	elif x.id == ATM__STM_SWI:
		unparseStmSwi(zCtx, depth, x.dat)
	elif x.id == ATM__JMP:
		unparseJmp(zCtx, depth, x.dat)
	elif x.id == ATM__CALL:
		unparseCall(zCtx, depth, x.dat)

	#unknown exe
	else:
		zCtx.int("Unknown ID " + str(x.id) + " in exe.", prtSubCtxs=False, prtLine=False)



#scope
def unparseScp(zCtx, depth, scope, skipFirstDIs=0):
	for di in scope.datItms:
		if skipFirstDIs != 0:
			skipFirstDIs -= 1
		else:
			unparseDclDat(zCtx, depth, di)
	for x in scope.header:
		unparseExe(zCtx, depth, x)
	for x in scope.exes:
		unparseExe(zCtx, depth, x)
	for x in scope.footer:
		unparseExe(zCtx, depth, x)



#fcts
def unparseFct(zCtx, f):
	zCtx.dbg0("Unparsing FCT " + f.toStr())

	#ext
	if f.ext:
		zCtx.cpl.resObv.append("ext" + OBV__SEP + f.name)

	#int
	else:
		res = ["fct" + OBV__SEP + f.name]

		#retType
		retTypeTxt = "void"
		if f.retType != TYPE_ID__UNKNOWN:
			retTypeTxt = zCtx.getTypeNameFromID(f.retType)

		#params
		paramsTxtFP = ""
		for p in range(len(f.params)):
			di     = f.params[p]
			diType = zCtx.getTypeInstanceFromID(di.Type)

			#rsv them
			res.append(RES__OUTPUT_TAB + "rsv" + OBV__SEP + '_' + di.name + OBV__SEP + hexOnN(diType.dcnCommon.size, 4))

			#set them according to regs
			res.append(RES__OUTPUT_TAB + "r2d" + OBV__SEP + 'p' + str(p+1) + OBV__SEP + '_' + di.name)

			#fp
			paramsTxtFP += ',' + diType.name

		#output
		zCtx.cpl.resObv += res

		#fp
		if f.isPub:
			zCtx.cpl.resFP += 'f' + f.name + '\t' + retTypeTxt + paramsTxtFP + '\n'

		#content
		unparseScp(zCtx, 1, f.scope, skipFirstDIs=len(f.params))
	zCtx.dbg0("Unparsed FCT.")



#types
def unparseTypesFP(zCtx):
	zCtx.dbg0("Types ID table: " + zCtx.listTypeNames())
	refDcnCommon = zCtx.getTypeInstanceFromID(zCtx.refType).dcnCommon
	for tID in range(len(zCtx.cpl.types)):
		tInst = zCtx.cpl.types[tID]
		tFP   = ""
		zCtx.dbg0("Unparsing DCL TYP " + tInst.name)

		#skip root types
		if tID in zCtx.rootTypes or \
			tID == zCtx.gncDcnType or \
			tID == zCtx.refType or \
			tID in zCtx.spcDcnTypes:
			continue

		#skip ref types (dcn)
		if tInst.dcnCommon == refDcnCommon:
			continue

		#shared type
		if not tInst.ext:
			tFP += 't' + tInst.name + '\t'

			#prm
			if tInst.dcnCommon.nature == NATURE__PRM:
				tFP += 'p' + zCtx.getTypeNameFromID(tInst.dcnCommon.parent)

			#stc
			elif tInst.dcnCommon.nature == NATURE__STC:
				tFP += 's'
				for f in tInst.dcnCommon.fields:
					tFP += zCtx.getTypeNameFromID(f.Type) + ',' + f.name + ','
				tFP = str_sub(tFP, stop=-2)

		#output
		zCtx.cpl.resFP += tFP
		zCtx.dbg0("Unparsed DCL TYP.")






# -------- EXECUTION --------

#main
def c07_unparseAsObv(zCtx):
	zCtx.updateLogLvl(STEP.C07)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("======================= C07 UNPARSE AS OBVIOUS : beginning ======================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#some help lines on top
	zCtx.cpl.resObv += readFile(CXD + "/help-header.obv").split('\n')

	#gbl scp: obv
	unparseScp(zCtx, 0, zCtx.cpl.gblScp)

	#gbl scp: fp, types
	unparseTypesFP(zCtx)

	#gbl scp: fp, datItms
	for di in zCtx.cpl.gblScp.datItms:
		if not di.ext and di.isPub:
			zCtx.cpl.resFP += 'd' + di.name + '\t' + zCtx.getTypeNameFromID(di.Type)

	#fcts
	for f in zCtx.cpl.fcts:
		if f.content is None: #compiled fcts only (leave dcp-dep aside)
			unparseFct(zCtx, f)

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("======================= C07 UNPARSE AS OBVIOUS : end ======================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c07.obv", '\n'.join(zCtx.cpl.resObv))

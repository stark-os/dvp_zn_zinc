#!/usr/bin/python3



# -------- IMPORTATIONS --------

# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< should be already shared from src/main.z, Pythonic
import sys, os
CXD = os.path.dirname(os.path.realpath(sys.argv[0]))

#internal
from zctx import *

#obv
from obv.src.exe import *
from obv.src.val import *






# -------- SPECIFIC UNPARSE --------

#value
def unparseVal(zCtx, depth, v):
	zCtx.dbg1("Unparsing VAL " + v.toStr(depth=1))

	#value type gives sz (in bits!)
	obvSz = 8 * zCtx.getTypeInstanceFromID(v.Type).dcnCommon.size

	#lit int
	if v.vdat.id in (ATM__S8,  ATM__U8):
		zCtx.dbg1("Unparsed VAL (lit 8b).")
		return obvVal(OBV_VAL__LIT,  obvSz, hexOnN(v.vdat.dat, 2))
	if v.vdat.id in (ATM__S16, ATM__U16):
		zCtx.dbg1("Unparsed VAL (lit 16b).")
		return obvVal(OBV_VAL__LIT, obvSz, hexOnN(v.vdat.dat, 4))
	if v.vdat.id in (ATM__S32, ATM__U32):
		zCtx.dbg1("Unparsed VAL (lit 32b).")
		return obvVal(OBV_VAL__LIT, obvSz, hexOnN(v.vdat.dat, 8))
	if v.vdat.id in (ATM__S64, ATM__U64):
		zCtx.dbg1("Unparsed VAL (lit 64b).")
		return obvVal(OBV_VAL__LIT, obvSz, hexOnN(v.vdat.dat, 16))

	#datItm
	if v.vdat.id == ATM__DATITM:
		name  = '_'*(depth+1) + v.vdat.dat.name
		zCtx.dbg1("Unparsed VAL (datItm).")
		return obvVal(OBV_VAL__DATITM, obvSz, name + "+0000")

	#call
	if v.vdat.id == ATM__CALL:
		unparseCall(zCtx, depth, v.vdat.dat)
		zCtx.dbg1("Unparsed VAL (call).")
		return obvVal(OBV_VAL__REG, obvSz, "r")

	#ffa
	if v.vdat.id == ATM__FFA:
		ov = unparseVal(zCtx, depth, v.vdat.dat.value)
		if ov.kind != OBV_VAL__DATITM:
			zCtx.int("Still have FFA value on a non-datItm val " + v.vdat.dat.value.toStr(), prtSubCtxs=False, prtLine=False)

		#remove prev 0 offset, to set ours
		plusIdx     = str_findFirstChr(ov.txt, '+')
		nameAndPlus = str_sub(ov.txt, stop=plusIdx)

		#int err
		prevOffset = str_sub(ov.txt, start=plusIdx+1)
		if prevOffset != "0000":
			zCtx.int("Got non-zero offset in datItm used in FFA => SHOULDN'T BE!")

		#res
		return obvVal(OBV_VAL__DATITM, obvSz, nameAndPlus + hexOnN(v.vdat.dat.offset, 4))

	#frf
	if v.vdat.id == ATM__FRF:
		name  = '_'*(depth+1) + v.vdat.dat.di.name
		return obvVal(OBV_VAL__PTR, obvSz, name + "+0000")

	#unknown
	zCtx.int("Unknown ID " + str(v.vdat.id) + " in value " + v.toStr(), prtSubCtxs=False, prtLine=False)
	return obvVal(OBV_VAL__UNKNOWN, obvSz, "") #unreachable



#datItm
def unparseDclDat(zCtx, depth, di):
	zCtx.dbg1("Unparsing DCL DAT.")
	begBlanks = OBV__SEP * depth

	#sizes
	sz    = zCtx.getTypeInstanceFromID(di.Type).dcnCommon.size #Z size (in bytes)
	rsvSz = hexOnN(sz, 4) #size for "rsv" OBV ist (in bytes)
	obvSz = 8 * sz        #size for OBV operation ist (in bits)

	#obv-pfxed name
	name = '_'*(depth+1) + di.name

	#initVal (should not have any at this point... but anyway)
	if di.inited:
		ov  = unparseVal(zCtx, depth, di.initVal)
		ist = "DDD"
		if ov.kind == OBV_VAL__LIT:
			ist = "v2d"
		elif ov.kind == OBV_VAL__DATITM:
			ist = "d2d"
		elif ov.kind == OBV_VAL__REG:
			ist = "r2d"
		elif ov.kind == OBV_VAL__PTR:
			ist = "p2d"
		zCtx.cpl.resObv.exes.append(obvExe( ist, obvSz, [ov.txt, name], begBlanks ))

	#rsv
	zCtx.cpl.resObv.exes.append(obvExe( "rsv", obvSz, [name, rsvSz], begBlanks ))
	zCtx.dbg1("Unparsed DCL DAT.")



#asg

#upcasting => write full 0 in dst before writing the fewer bytes of src
def upcasting(zCtx, srcOV, dstOV, begBlanks):
	if srcOV.sz < dstOV.sz:
		zeroTxt = "00" * (dstOV.sz >> 3) # <=> "/8"

		#can be either REG or DATITM (other cases are managed by upper parsing levels)
		dstKind = 'U'
		if dstOV.kind == OBV_VAL__DATITM:
			dstKind = 'd'
		elif dstOV.kind == OBV_VAL__REG:
			dstKind = 'r'
		zCtx.cpl.resObv.exes.append(obvExe( "v2" + dstKind, dstOV.sz, [zeroTxt, dstOV.txt], begBlanks ))

def unparseAsg(zCtx, depth, a):
	zCtx.dbg1("Unparsing ASG " + a.toStr(depth=1))
	begBlanks = OBV__SEP * depth

	#src, dst
	srcOV = unparseVal(zCtx, depth, a.src)
	dstOV = unparseVal(zCtx, depth, a.dst)

	#upcasting if needed
	upcasting(zCtx, srcOV, dstOV, begBlanks)

	#ist: src
	ist = "A"
	if srcOV.kind == OBV_VAL__LIT:
		ist = 'v'
	elif srcOV.kind == OBV_VAL__DATITM:
		ist = 'd'
	elif srcOV.kind == OBV_VAL__REG:
		ist = 'r'
	elif srcOV.kind == OBV_VAL__PTR:
		ist = 'p'
	ist += '2'

	#ist: dst
	if dstOV.kind == OBV_VAL__LIT:
		zCtx.int("Got assignment into a literal value (makes no sens) " + a.toStr(), prtSubCtxs=False, prtLine=False)
	elif dstOV.kind == OBV_VAL__REG:
		ist += 'r'
	elif dstOV.kind == OBV_VAL__DATITM:
		ist += 'd'
	elif dstOV.kind == OBV_VAL__PTR:
		zCtx.int("Got assignment into a pointer value (makes no sens) " + a.toStr(), prtSubCtxs=False, prtLine=False)

	#res
	zCtx.cpl.resObv.exes.append(obvExe( ist, srcOV.sz, [srcOV.txt, dstOV.txt], begBlanks ))
	zCtx.dbg1("Unparsed ASG.")



#stm if
def TMP_COND_UNPARSE(zCtx, ov, begBlanks):
	kindTxt = 'U'
	if ov.kind == OBV_VAL__LIT:
		kindTxt = 'L'
	elif ov.kind == OBV_VAL__DATITM:
		kindTxt = 'D'
	elif ov.kind == OBV_VAL__REG:
		kindTxt = 'R'
	elif ov.kind == OBV_VAL__PTR:
		kindTxt = 'P'
	zCtx.cpl.resObv.exes.append(obvExe( "CMP", 0, [kindTxt + ':' + ov.txt], begBlanks ))

def unparseStmIf(zCtx, depth, i, begEnd=True):
	zCtx.dbg1("Unparsing IF " + i.toStr(depth=1))
	begBlanks = OBV__SEP * depth

	#condition
	condOV = unparseVal(zCtx, depth, i.cond)
	TMP_COND_UNPARSE(zCtx, condOV, begBlanks)

	#ok
	unparseScp(zCtx, depth+1, i.ifScope)

	#ko
	if i.elsScope is not None:
		unparseScp(zCtx, depth+1, i.elsScope)
	zCtx.dbg1("Unparsed IF.")



#whi
def unparseStmWhi(zCtx, depth, w, begEnd=True):
	zCtx.dbg1("Unparsing WHI " + w.toStr(depth=1))
	begBlanks = OBV__SEP * depth

	#iterCond
	condOV = unparseVal(zCtx, depth, w.iterCond)
	TMP_COND_UNPARSE(zCtx, condOV, begBlanks)

	#scope
	unparseScp(zCtx, depth+1, w.scope)
	zCtx.dbg1("Unparsed WHI.")



#swi
def unparseStmSwi(zCtx, depth, s, begEnd=True):
	zCtx.dbg1("Unparsing SWI " + s.toStr(depth=1))
	begBlanks = OBV__SEP * depth

	#tgt
	tgtOV = unparseVal(zCtx, s.tgt, depth)
	TMP_COND_UNPARSE(zCtx, tgtOV, begBlanks)

	#for each case
	c = 0
	while c < len(s.cases):

		#case cond
		caseOV = unparseVal(zCtx, depth, s.cases[c])
		TMP_COND_UNPARSE(zCtx, caseOV, begBlanks)

		#case scope
		unparseScp(zCtx, depth+1, s.scopes[c])
		c += 1

	#def case
	if len(s.scopes) > len(s.cases):
		unparseScp(zCtx, depth+1, s.scopes[c])
	zCtx.dbg1("Unparsed SWI.")



#jmp
def unparseJmp(zCtx, depth, j):
	zCtx.dbg1("Unparsing JMP " + j.toStr(depth=1))
	begBlanks = OBV__SEP * depth

	#brk
	if j.kind == JMP__BRK:
		zCtx.cpl.resObv.exes.append(obvExe( "BRK", 0, [], begBlanks ))

	#ctn
	if j.kind == JMP__CTN:
		zCtx.cpl.resObv.exes.append(obvExe( "CTN", 0, [], begBlanks ))

	#ret
	if j.kind == JMP__RET:
		if j.retVal is not None:
			retValOV = unparseVal(zCtx, depth, j.retVal)

			#sizes, obv format
			regObvSz     = 8 * zCtx.smaxSize
			retTypeObvSz = 8 * zCtx.getTypeInstanceFromID(j.tgtFct.retType).dcnCommon.size

			#ret type bigger than ARCH SIZE => PROBLEM, BUT SHOULD NOT BE <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
			#if retTypeObvSz > regObvSz:
			#	zCtx.int("Still having return value greater than arch size (" + str(retTypeObvSz) + " > " + str(regObvSz) + ") in call " + c.toStr(), prtSubCtxs=False, prtLine=False)

			#upcasting if needed
			upcasting(zCtx,
				retValOV,
				obvVal(OBV_VAL__REG, retTypeObvSz, "r"), #VERY IMPORTANT: We upcast depending on the FCT RET TYPE targetted: fct a() s16 { ret `b2 } => upcasted as s16 and not as ARCH_SIZE!
				begBlanks                                #The remaining part of "r" will stay unchanged, but we don't care because res will only have its first 16b used in upper scope (as a regular s16).
			)
			obvSz = retTypeObvSz #therefore, here is the real sz on which we are going to write into paramReg

			#set ret val
			ist = "JJJ"
			if retValOV.kind == OBV_VAL__LIT:
				ist = "v2r"
			elif retValOV.kind == OBV_VAL__DATITM:
				ist = "d2r"
			elif retValOV.kind == OBV_VAL__REG:
				ist = "r2r"
			elif retValOV.kind == OBV_VAL__PTR:
				ist   = "p2r"
				obvSz = regObvSz
			zCtx.cpl.resObv.exes.append(obvExe( ist, obvSz, [retValOV.txt, "r"], begBlanks ))

		#ret
		zCtx.cpl.resObv.exes.append(obvExe( "bck", 0, [], begBlanks ))
	zCtx.dbg1("Unparsed JMP.")



#call
def unparseCall(zCtx, depth, c):
	zCtx.dbg1("Unparsing CALL " + c.toStr(depth=1))
	begBlanks = OBV__SEP * depth

	#too much params
	if len(c.paramVals) > len(OBV__PARAMS):
		zCtx.err("Too much parameters to function call \"" + c.name + "\" (maximum " + str(len(OBV__PARAMS)) + " allowed, got " + str(len(c.paramVals)) + ").", prtSubCtxs=False, prtLine=False)

	#targetted fct
	tgtFct = None
	for f in zCtx.cpl.fcts:
		if f.name == c.name:
			tgtFct = f
			break
	if tgtFct is None:
		zCtx.int("Got a call to non-existing fct \"" + c.name + "\", " + c.toStr())

	#params
	regObvSz = zCtx.smaxSize << 3
	for p in range(len(c.paramVals)):
		paramReg = OBV__PARAMS[p]

		#sub-calls => forbidden! Cannot safely set all pX registers if a subcall uses them in between!
		paramValOV = unparseVal(zCtx, depth, c.paramVals[p])
		if paramValOV.kind == OBV_VAL__REG:
			zCtx.int("Still having subcalls when unparsing in OBV call " + c.toStr(), prtSubCtxs=False, prtLine=False)

		#fct expected param sz & given param sz
		tgtFct_paramObvSz = zCtx.getTypeInstanceFromID(tgtFct.params[p].Type).dcnCommon.size << 3
		paramObvSz        = zCtx.getTypeInstanceFromID(  c.paramVals[p].Type).dcnCommon.size << 3

		#still having big paramVals => problem in previous cpl steps
		if paramObvSz > regObvSz:
			zCtx.int("Still having call parameter " + str(p+1) + " greater than arch size (" + str(paramObvSz) + " > " + str(regObvSz) + ") in call " + c.toStr(), prtSubCtxs=False, prtLine=False)

		#however, big params in fct itself => OK, we will just ensure to upcast them until #ref only
		if tgtFct_paramObvSz > regObvSz:
			tgtFct_paramObvSz = regObvSz

		#upcasting if needed
		upcasting(zCtx,
			paramValOV,
			obvVal(OBV_VAL__REG, tgtFct_paramObvSz, paramReg), #VERY IMPORTANT: We upcast depending on the FCT PARAM TYPE targetted: fct a(s16 b) {...}; a(`b2) => upcasted as s16 and not as ARCH_SIZE!
			begBlanks                                          #The remaining part of the paramReg will stay unchanged, but we don't care because fct content will only use its first 16b (as a regular s16).
		)
		obvSz = tgtFct_paramObvSz #therefore, here is the real sz on which we are going to write into paramReg

		#set param reg
		if paramValOV.kind == OBV_VAL__LIT:
			ist = "v2r"
		elif paramValOV.kind == OBV_VAL__DATITM:
			ist = "d2r"
		elif paramValOV.kind == OBV_VAL__PTR:
			ist   = "p2r"
			obvSz = regObvSz #use whole reg if passing REF instead of actual value
		zCtx.cpl.resObv.exes.append(obvExe( ist, obvSz, [paramValOV.txt, paramReg], begBlanks ))

	#ivq
	zCtx.cpl.resObv.exes.append(obvExe( "ivq", 0, [c.name], begBlanks ))
	zCtx.dbg1("Unparsed CALL.")






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
	elif x.id == ATM__OBVEXE:
		zCtx.cpl.resObv.exes.append(x.dat)

	#unknown exe
	else:
		zCtx.int("Unknown ID " + str(x.id) + " in exe.", prtSubCtxs=False, prtLine=False)



#scope
def unparseScp(zCtx, depth, scope):
	for di in scope.datItms:
		unparseDclDat(zCtx, depth, di)
	for x in scope.header:
		unparseExe(zCtx, depth, x)
	for x in scope.exes:
		unparseExe(zCtx, depth, x)
	for x in scope.footer:
		unparseExe(zCtx, depth, x)



#fcts
def unparseFct(zCtx, f):
	zCtx.dbg0("Unparsing FCT " + f.name)
	if not f.ext:

		#obv exe
		zCtx.cpl.resObv.exes.append(obvExe( "fct", 0, [f.name], "" ))

		#retType (FP)
		retTypeTxtFP = "void"
		if f.retType != TYPE_ID__UNKNOWN:
			retTypeTxtFP = zCtx.getTypeNameFromID(f.retType)

		#params (FP)
		paramsTxtFP = ""
		for p in range(len(f.params)):
			paramsTxtFP += ',' + zCtx.getTypeNameFromID(f.params[p].Type)

		#fp
		if f.isPub:
			accessPfx = 'u'
		elif zCtx.cpl.opts["INCLUDE_PRV_IN_FP"] == "ON":
			accessPfx = 'r'
		zCtx.cpl.resFP += accessPfx + 'f' + f.name + '\t' + retTypeTxtFP + paramsTxtFP + '\n'

		#content
		unparseScp(zCtx, 1, f.scope)
	zCtx.dbg0("Unparsed FCT.")



#types
def unparseTypesFP(zCtx):
	refDcnCommon = zCtx.getTypeInstanceFromID(zCtx.refType).dcnCommon
	undcnFP = []
	dcnFP   = []
	for tID in range(len(zCtx.cpl.types)):
		tInst = zCtx.cpl.types[tID]
		zCtx.dbg1("Unparsing DCL TYP " + tInst.name)

		#skip root types
		if tID in zCtx.rootTypes or \
			tID == zCtx.gncDcnType or \
			tID == zCtx.refType or \
			tID in zCtx.spcDcnTypes:
			continue

		#skip ref types (dcn)
		#if tInst.dcnCommon == refDcnCommon: <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		#	continue

		#int type
		if not tInst.ext:
			dcnDegTxt = ',' + str(tInst.dcnCommon.dcnDeg)

			#sharing access
			acsPfx = 'u'
			if not tInst.dcnCommon.isPub:
				if zCtx.cpl.opts["INCLUDE_PRV_IN_FP"] == "ON":
					acsPfx = 'r'
				else:
					continue

			#common beg
			line = acsPfx + 't' + tInst.name + '\t'

			#case 1: dcned
			if len(tInst.dcns) != 0:
				line += 'd' + dcnDegTxt
				for dcnID in tInst.dcns:
					line += ',' + zCtx.getTypeNameFromID(dcnID)
				dcnFP.append(line)

			#case 2: stc
			elif tInst.dcnCommon.nature == NATURE__STC:
				line += 's' + dcnDegTxt
				for f in tInst.dcnCommon.fields:
					line += ',' + zCtx.getTypeNameFromID(f.Type) + ':' + f.name
				undcnFP.append(line)

			#case 3: enm
			elif tInst.dcnCommon.nature == NATURE__ENM:
				line += 'e' + dcnDegTxt
				for f in tInst.dcnCommon.fields:
					line += ',' + f.name
				undcnFP.append(line)

			#everything else => can be only a type copy of a primitive
			else:
				undcnFP.append(line + 'c' + dcnDegTxt + ',' + zCtx.getTypeNameFromID(tInst.parent))

	#output
	zCtx.cpl.resFP += '\n'.join(undcnFP) + '\n' + '\n'.join(dcnFP) + '\n'
	zCtx.dbg1("Unparsed DCL TYPs.")

#gbl datItms
def unparseGblDatItmsFP(zCtx):
	for di in zCtx.cpl.gblScp.datItms:
		if not di.ext:

			#shared access
			dFP = ""
			if di.isPub:
				dFP = "ud" + di.name + '\t' + zCtx.getTypeNameFromID(di.Type) + '\n'
			elif zCtx.cpl.opts["INCLUDE_PRV_IN_FP"] == "ON":
				dFP = 'r' + str_sub(dFP, start=1)

			#output
			zCtx.cpl.resFP += dFP






# -------- EXECUTION --------

#main
def c08_unparseAsObv(zCtx):
	zCtx.updateLogLvl(STEP.C08)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("======================= C08 UNPARSE AS OBVIOUS : beginning ======================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#gbl scp: obv
	unparseScp(zCtx, 0, zCtx.cpl.gblScp)

	#gbl scp: types FP
	unparseTypesFP(zCtx)

	#gbl scp: datItms FP
	unparseGblDatItmsFP(zCtx)

	#fcts
	for f in zCtx.cpl.fcts:
		if f.content is None: #compiled fcts only (leave dcp-dep aside)
			unparseFct(zCtx, f)

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("======================= C08 UNPARSE AS OBVIOUS : end ======================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#write out obv res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c08.obv", zCtx.cpl.resObv.unparse())

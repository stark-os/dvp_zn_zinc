#!/usr/bin/python3



# -------- IMPORTATIONS --------

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

	#stc
	if v.vdat.id == ATM__FMAP_STR_VAL:
		res = "<FMAP__STR_VAL> #not implemented yet"
		'''
		for k in v.vdat.dat.keys():
			zCtx.cpl.resC += '.' + k + '='
			unparseVal(zCtx, v.vdat.dat[k], depth)
			zCtx.cpl.resC += ','
		zCtx.cpl.resC = str_sub(zCtx.cpl.resC, stop=-2) #these 2 lines in Z: "zCtx.cpl.resC[-1] = '}'" <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		zCtx.cpl.resC += '}'
		'''
		return (OBV__VAL_LIT, res)

	#ffa
	if v.vdat.id == ATM__FFA:
		obvValType, txt = unparseVal(zCtx, depth, v.vdat.dat.value)
		if obvValType != OBV__VAL_DATITM:
			zCtx.int("Still have FFA value on a non-datItm val " + v.vdat.dat.value.toStr(), prtSubCtxs=False, prtLine=False)
		return (OBV__VAL_DATITM, txt + '+' + hexOnN(v.vdat.dat.offset, 4))

	#unknown
	zCtx.int("Unknown ID " + str(v.vdat.id) + " in value " + v.toStr(), prtSubCtxs=False, prtLine=False)
	return (OBV__VAL__UNKNOWN, "") #unreachable



#datItm
def unparseDclDat(zCtx, depth, di):
	zCtx.dbg0("Unparsing DCL DAT.")
	d   = RES__OUTPUT_TAB * depth
	res = ""

	#type size
	sizeTxt = hexOnN(zCtx.getTypeInstanceFromID(di.Type).dcnCommon.size, 4)

	#pfx name
	name = '_'*(depth+1) + di.name

	#rsv
	res = d + "rsv" + OBV__SEP + name + OBV__SEP + sizeTxt + '\n'

	#initVal
	if di.inited:
		res += d
		obvValType, txt = unparseVal(zCtx, depth, di.initVal)
		if obvValType == OBV__VAL_LIT:
			res += "v2d" + OBV__SEP + name + OBV__SEP + txt + '\n'
		elif obvValType == OBV__VAL_DATITM:
			res += "d2d" + OBV__SEP + name + OBV__SEP + txt + sizeTxt + '\n'
		elif obvValType == OBV__VAL_REG:
			res += "r2d" + OBV__SEP + name + OBV__SEP + txt + '\n'

	#output
	zCtx.cpl.resObv += res
	zCtx.dbg0("Unparsed DCL DAT.")



#asg
def unparseAsg(zCtx, depth, a):
	zCtx.dbg0("Unparsing ASG " + a.toStr(depth=1))
	d   = RES__OUTPUT_TAB * depth
	res = ""

	#src
	srcObvType, srcValTxt = unparseVal(zCtx, depth, a.src)

	#dst
	dstObvType, dstValTxt = unparseVal(zCtx, depth, a.dst)
	dstSizeTxt            = hexOnN(zCtx.getTypeInstanceFromID(a.dst.Type).dcnCommon.size, 4)

	#invalid dst
	if dstObvType == OBV__VAL_LIT:
		zCtx.int("Got assignment into a literal value (makes no sens) " + a.toStr())
	res += d

	#write: from lit
	if srcObvType == OBV__VAL_LIT:
		if dstObvType == OBV__VAL_DATITM:
			res += "v2d" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt + '\n'
		if dstObvType == OBV__VAL_REG:
			res += "v2r" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt + '\n'

	#write: from
	elif srcObvType == OBV__VAL_DATITM:
		if dstObvType == OBV__VAL_DATITM:
			res += "d2d" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt + OBV__SEP + dstSizeTxt + '\n'
		if dstObvType == OBV__VAL_REG:
			res += "d2r" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt + '\n'

	#write: from register
	else:
		if dstObvType == OBV__VAL_DATITM:
			res += "r2d" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt + '\n'
		if dstObvType == OBV__VAL_REG:
			res += "r2r" + OBV__SEP + srcValTxt + OBV__SEP + dstValTxt + '\n'

	#output
	zCtx.cpl.resObv += res
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
	res = ""

	#brk
	if j.kind == JMP__BRK:
		res += d + "BREAK\n"

	#ctn
	if j.kind == JMP__CTN:
		res += d + "CONTINUE\n"

	#ret
	if j.kind == JMP__RET:
		if j.retVal is not None:
			res += d
			obvValType, txt = unparseVal(zCtx, depth, j.retVal)
			if obvValType == OBV__VAL_LIT:
				res += "v2r"
			if obvValType == OBV__VAL_DATITM:
				res += "d2r"
			else:
				res += "r2r"
			res += OBV__SEP + txt + "r\n"
		res += d + "bck\n"

	#output
	zCtx.cpl.resObv += res
	zCtx.dbg0("Unparsed JMP.")



#call
def unparseCall(zCtx, depth, c):
	zCtx.dbg0("Unparsing CALL " + c.toStr(depth=1))
	d   = RES__OUTPUT_TAB * depth
	res = ""

	#params
	for p in range(len(c.paramVals)):
		res += d
		obvValType, txt = unparseVal(zCtx, depth, c.paramVals[p])
		if obvValType == OBV__VAL_LIT:
			res += "v2r"
		elif obvValType == OBV__VAL_DATITM:
			res += "d2r"
		else:
			res += "r2r"
		res += OBV__SEP + txt + OBV__SEP + 'p' + str(p+1) + '\n'

	#ivq
	res += d + "ivq" + OBV__SEP + c.name + '\n'

	#back
	res += d + "bck\n"

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
		zCtx.cpl.resObv += "ext" + OBV__SEP + f.name + '\n'

	#int
	else:
		res = "fct" + OBV__SEP + f.name + '\n'

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
			res += RES__OUTPUT_TAB + "rsv" + OBV__SEP + '_' + di.name + OBV__SEP + hexOnN(diType.dcnCommon.size, 4) + '\n'

			#set them according to regs
			res += RES__OUTPUT_TAB + "r2d" + OBV__SEP + 'p' + str(p+1) + OBV__SEP + '_' + di.name + '\n'

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
		if tID in zCtx.rootTypes or tID == zCtx.gncDcnType or tID == zCtx.refType or tID in zCtx.spcDcnTypes:
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
def c08_unparseAsObv(zCtx):
	zCtx.updateLogLvl(STEP.C08)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("======================= C08 UNPARSE AS OBVIOUS : beginning ======================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#some help lines on top
	zCtx.cpl.resObv += "# ---------------- HELP SHORT ----------------\n"
	zCtx.cpl.resObv += "#\n# Syntax:\n"
	zCtx.cpl.resObv += "# - Everything written after a hash '#' will be ignored until the end of line.\n"
	zCtx.cpl.resObv += "# - Space and tabulation characters are ignored at beginning and end of each line.\n"
	zCtx.cpl.resObv += "# - Empty lines are ignored.\n"
	zCtx.cpl.resObv += "# - EVERY data value is given in the following format:\n"
	zCtx.cpl.resObv += "#   > An even number of lowercase hexadecimal digits.\n"
	zCtx.cpl.resObv += "#   > Each pair of hexadecimal digit corresponds to a byte.\n"
	zCtx.cpl.resObv += "# - .\n"
	zCtx.cpl.resObv += "#\n# Data items:\n"
	zCtx.cpl.resObv += "# - User data items are stored EXLUSIVELY in the stack.\n"
	zCtx.cpl.resObv += "# - Their names are prefixed by underscores '_' according to their scope.\n"
	zCtx.cpl.resObv += "#   The deepest the scope is, the more it will have underscores in prefix.\n"
	zCtx.cpl.resObv += "#   Global scope data items starts with 1 underscore as prefix.\n"
	zCtx.cpl.resObv += "# - Data items are always refered using their name followed by an offset suffix.\n"
	zCtx.cpl.resObv += "#   An offset suffix is a plus sign '+' followed by 4 hex digits.\n"
	zCtx.cpl.resObv += "#   This way, you are refering to a \"stack location\".\n"
	zCtx.cpl.resObv += "#   This is the only way to interact with the stack.\n"
	zCtx.cpl.resObv += "#\n# Registers:\n"
	zCtx.cpl.resObv += "# - Registers are some special memory locations you can use to read/write from.\n"
	zCtx.cpl.resObv += "# - There is a fixed amount of them, each with its specific use.\n"
	zCtx.cpl.resObv += "# - Every register is 4 or 8 bytes long, depending on the architecture targetted (64=8B).\n"
	zCtx.cpl.resObv += "#   Therefore, every operation made with them implies working with the whole memory chunk.\n"
	zCtx.cpl.resObv += "# - All the registers available here are:\n"
	zCtx.cpl.resObv += "#   > p1,p2,p3,p4,p5,p6 corresponds to function parameters.\n"
	zCtx.cpl.resObv += "#   > r                 corresponds to function return value.\n"
	zCtx.cpl.resObv += "#\n# Instructions:\n"
	zCtx.cpl.resObv += "#   Stack:\n"
	zCtx.cpl.resObv += "#   - rsv = \"reserve\"\n"
	zCtx.cpl.resObv += "#     Making place in the stack for some bytes, now accessible via the data item name given.\n#\n"
	zCtx.cpl.resObv += "#   - v2d = \"value to data item write\"\n"
	zCtx.cpl.resObv += "#     Write bytes given into a stack location.\n#\n"
	zCtx.cpl.resObv += "#   - d2d = \"data item to data item write\"\n"
	zCtx.cpl.resObv += "#     Write from a stack location into another stack location, the given number of bytes.\n#\n"
	zCtx.cpl.resObv += "#   - r2d = \"register to data item write\"\n"
	zCtx.cpl.resObv += "#     Write from a register into a stack location.\n#\n"
	zCtx.cpl.resObv += "#   Registers:\n"
	zCtx.cpl.resObv += "#   - r2r = \"register to register write\"\n"
	zCtx.cpl.resObv += "#     Write from a register into a register.\n#\n"
	zCtx.cpl.resObv += "#   - v2r = \"value to register write\"\n"
	zCtx.cpl.resObv += "#     Write bytes given into a register.\n#\n"
	zCtx.cpl.resObv += "#   - d2r = \"data item to register write\"\n"
	zCtx.cpl.resObv += "#     Write from a stack location into a register.\n#\n"
	zCtx.cpl.resObv += "#   Functions:\n"
	zCtx.cpl.resObv += "#   - fct = \"function\"\n"
	zCtx.cpl.resObv += "#     Declares a function invocation starting point.\n#\n"
	zCtx.cpl.resObv += "#   - ivq = \"invoque\"\n"
	zCtx.cpl.resObv += "#     Pause current function execution, and move to the new function starting point given.\n#\n"
	zCtx.cpl.resObv += "#   - bck = \"back\"\n"
	zCtx.cpl.resObv += "#     Stop current function execution, and resume it back, right after we were invoqued.\n#\n"
	zCtx.cpl.resObv += "#   - ext = \"external\"\n"
	zCtx.cpl.resObv += "#     Mentions a function used by the program, but not declared in it.\n#\n"
	zCtx.cpl.resObv += "# --------------------------------------------\n\n"

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

	#final msg if everything went OK, still cool to have that info
	zCtx.dbg0("Types ID table: " + zCtx.listTypeNames())

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("======================= C08 UNPARSE AS OBVIOUS : end ======================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

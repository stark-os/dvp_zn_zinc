#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- SPECIFIC UNPARSE --------

#type
def unparseType(zCtx, tID):

	#skip root types, ref & dcn keywords
	if tID in zCtx.rootTypes or tID == zCtx.gncDcnType  or tID == zCtx.refType or tID in zCtx.spcDcnTypes:
		return

	#ref[dcn]
	refDcnCommon = zCtx.getTypeInstanceFromID(zCtx.refType).dcnCommon
	tInst        = zCtx.getTypeInstanceFromID(tID)
	if tInst.dcnCommon == refDcnCommon:
		zCtx.cpl.resC  += "typedef GUref " + tInst.name + ";\n"
		zCtx.cpl.resFP += 't' + tInst.name + "\tpGUref\n"
		zCtx.cpl.resFP_C += "typedef GUref " + tInst.name + ";\n" #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TMP
		return

	#beginning
	zCtx.dbg0("Unparsing TYP DCL " + tInst.name)
	typDcl    = ""
	typDcl_fp = 't' + tInst.name + '\t'

	#"typedef parentName name;"
	if tInst.dcnCommon.nature == NATURE__PRM:
		typDcl    += "typedef " + zCtx.getTypeNameFromID(tInst.dcnCommon.parent) + ' ' + tInst.name + ";\n"
		typDcl_fp += 'p' + zCtx.getTypeNameFromID(tInst.dcnCommon.parent)

	#"typedef struct { fieldType fieldName; ...} name;"
	elif tInst.dcnCommon.nature == NATURE__STC:
		typDcl += "typedef struct {"
		typDcl_fp += 's'

		#for each field
		for f in tInst.dcnCommon.fields:
			fieldTypeName = zCtx.getTypeNameFromID(f.Type)
			typDcl    += '\n' + RES__OUTPUT_TAB + fieldTypeName + ' ' + f.name + ';'
			typDcl_fp += fieldTypeName + ',' + f.name + ','

		#remake the end
		typDcl    += "\n} " + tInst.name + ";\n"
		typDcl_fp  = str_sub(typDcl_fp, stop=-2)

	#enm
	else:
		typDcl_fp += 'e'
		for f in tInst.dcnCommon.fields:
			typDcl_fp += f.name + ','
		typDcl_fp = str_sub(typDcl_fp, stop=-2)

	#fp
	if not tInst.ext and tInst.dcnCommon.isPub:
		zCtx.cpl.resFP   += typDcl_fp + '\n'
		zCtx.cpl.resFP_C += typDcl #<<<<<<<<<<<<<<<<<<< TMP

	#end
	zCtx.cpl.resC += typDcl
	zCtx.dbg0("Unparsed TYP DCL.")



#value
def unparseVal(zCtx, v, depth, casht=False):
	zCtx.dbg0("Unparsing VAL " + v.toStr(depth=1))

	#cast res
	if casht:
		zCtx.cpl.resC += '(' + zCtx.getTypeNameFromID(v.Type) + ")("

	#lit int
	if v.vdat.id in (ATM__S8,  ATM__U8):
		zCtx.cpl.resC += "0x" + hexOnN(v.vdat.dat, 2)
	elif v.vdat.id in (ATM__S16, ATM__U16):
		zCtx.cpl.resC += "0x" + hexOnN(v.vdat.dat, 4)
	elif v.vdat.id in (ATM__S32, ATM__U32):
		zCtx.cpl.resC += "0x" + hexOnN(v.vdat.dat, 8)
	elif v.vdat.id in (ATM__S64, ATM__U64):
		zCtx.cpl.resC += "0x" + hexOnN(v.vdat.dat, 16)

	#datItm
	elif v.vdat.id == ATM__DATITM:
		zCtx.cpl.resC += v.vdat.dat.name

	#call
	elif v.vdat.id == ATM__CALL:
		unparseCall(zCtx, v.vdat.dat, depth, begEnd=False)

	#raw data
	elif v.vdat.id == ATM__LST_VAL:
		zCtx.cpl.resC += "{.len=" + str(len(v.vdat.dat)) + ",.dat={"
		for c in v.vdat.dat:
			zCtx.cpl.resC += "'\\x" + hexOnN(c.vdat.dat, 2) + "',"
		zCtx.cpl.resC = str_sub(zCtx.cpl.resC, stop=-2)
		zCtx.cpl.resC += '}}'

	#stc
	elif v.vdat.id == ATM__FMAP_STR_VAL:
		zCtx.cpl.resC += '{'
		for k in v.vdat.dat.keys():
			zCtx.cpl.resC += '.' + k + '='
			unparseVal(zCtx, v.vdat.dat[k], depth+1)
			zCtx.cpl.resC += ','
		zCtx.cpl.resC = str_sub(zCtx.cpl.resC, stop=-2) #these 2 lines in Z: "zCtx.cpl.resC[-1] = '}'" <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
		zCtx.cpl.resC += '}'

	#unknown
	else:
		zCtx.int("Unknown ID " + str(v.vdat.id) + " in value " + v.toStr(), prtSubCtxs=False, prtLine=False)

	#end
	if casht:
		zCtx.cpl.resC += ')'
	zCtx.dbg0("Unparsed VAL.")



#datItm
def unparseDatDcl(zCtx, di, depth, begEnd=True):
	zCtx.dbg0("Unparsing DAT DCL " + di.toStr(depth=1))
	d   = RES__OUTPUT_TAB * depth
	dcl = ""

	#beg mark (shift)
	if begEnd:
		dcl += d

	#"type name;"
	diTypeName = zCtx.getTypeNameFromID(di.Type)
	if di.Cst:
		dcl += "const "
	dcl += diTypeName + ' ' + di.name

	#ext
	if di.ext:
		zCtx.cpl.resC += "extern " + dcl

	#int
	else:

		#gbl only
		if depth == 0:

			#fp
			if di.isPub:
				zCtx.cpl.resFP   += 'd' + di.name + '\t' + diTypeName
				zCtx.cpl.resFP_C += dcl + ";\n" #<<<<<<<<<<<<<<<<<<< TMP

			#prv
			else:
				zCtx.cpl.resC += "static "

		#both gbl & lcl
		zCtx.cpl.resC += dcl

	#init val
	if di.inited:
		zCtx.cpl.resC += " = "
		unparseVal(zCtx, di.initVal, depth, casht=True)

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed DAT DCL.")



#asg
def unparseAsg(zCtx, a, depth, begEnd=True):
	zCtx.dbg0("Unparsing ASG " + a.toStr(depth=1))
	d = RES__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#"name = val;"
	unparseVal(zCtx, a.dst, depth)
	zCtx.cpl.resC += " = "
	unparseVal(zCtx, a.src, depth, casht=True)

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed ASG.")



#stm if
def unparseStmIf(zCtx, i, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"if(cond){scp}else if(cond){scp}else{scp}"
	zCtx.dbg0("Unparsing IF " + i.toStr(depth=1))
	d = RES__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#conditional blocks
	zCtx.cpl.resC += "if("
	unparseVal(zCtx, i.cond, depth+1)
	zCtx.cpl.resC += "){\n"
	unparseScope(zCtx, i.ifScope, depth=depth+1)
	if i.elsScope is not None:
		zCtx.cpl.resC += d + "}else{\n"
		unparseScope(zCtx, i.elsScope, depth=depth+1)
	zCtx.cpl.resC += d + "}\n"
	zCtx.dbg0("Unparsed IF.")



#whi
def unparseStmWhi(zCtx, w, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"while(cond){scp}"
	zCtx.dbg0("Unparsing WHI " + w.toStr(depth=1))
	d = RES__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d
	zCtx.cpl.resC += "while("

	#iterCond
	unparseVal(zCtx, w.iterCond, depth+1)
	zCtx.cpl.resC += "){\n"

	#scope
	unparseScope(zCtx, w.scope, depth=depth+1)
	zCtx.cpl.resC += d + "}\n"
	zCtx.dbg0("Unparsed WHI.")



#swi
def unparseStmSwi(zCtx, s, depth, begEnd=True):
	if depth == 0:
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
	unparseVal(zCtx, s.tgt, depth+1)
	zCtx.cpl.resC += "){\n"

	#for each case
	c = 0
	while c < len(s.cases):
		zCtx.cpl.resC += dp1 + "case "
		unparseVal(zCtx, s.cases[c], depth+2)
		zCtx.cpl.resC += ": {\n"
		unparseScope(zCtx, s.scopes[c], depth=depth+2)
		zCtx.cpl.resC += dp1 + "}\n"
		c += 1

	#def block
	if len(s.scopes) > len(s.cases):
		zCtx.cpl.resC += dp1 + "default: {\n"
		unparseScope(zCtx, s.scopes[c], depth=depth+2)
		zCtx.cpl.resC += dp1 + "}\n"
	zCtx.cpl.resC = d + "}\n"
	zCtx.dbg0("Unparsed SWI.")



#jmp
def unparseJmp(zCtx, j, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got JMP in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"break;", "continue;", "return ;", "return val;"
	zCtx.dbg0("Unparsing JMP " + j.toStr(depth=1))
	d = RES__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#redirect
	if j.kind == JMP__BRK:
		zCtx.cpl.resC += "break"
	if j.kind == JMP__CTN:
		zCtx.cpl.resC += "continue"
	if j.kind == JMP__RET:
		zCtx.cpl.resC += "return "
		if j.retVal is not None:
			unparseVal(zCtx, j.retVal, depth)

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed JMP.")



#call
def unparseCall(zCtx, c, depth, begEnd=True):

	#"name(p1,p2...);"
	zCtx.dbg0("Unparsing CALL " + c.toStr(depth=1))
	d = RES__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#name
	name = c.name
	if name == "frf":
		name = "&"
	zCtx.cpl.resC += name + "(\n"

	#params
	for p in c.paramVals:
		zCtx.cpl.resC += d + RES__OUTPUT_TAB
		unparseVal(zCtx, p, depth+1)
		zCtx.cpl.resC += ",\n"
	zCtx.cpl.resC = str_sub(zCtx.cpl.resC, stop=-3) + '\n' #immutable str in python, but in Z, we can simply make resC[-2] = ' ' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	zCtx.cpl.resC += d + ")"

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed CALL.")



#fct
def unparseFctHeader(zCtx, f):
	zCtx.dbg0("Unparsing FCT HEADER of " + f.toStr(depth=1))
	header = ""

	#retType
	retTypeTxt = "void"
	if f.retType != TYPE_ID__UNKNOWN:
		retTypeTxt = zCtx.getTypeNameFromID(f.retType)

	#"retType name(p1type p1name, ...) {"
	paramsTxt_C  = ""
	paramsTxt_FP = ""
	for p in f.params:
		pTypeName     = zCtx.getTypeNameFromID(p.Type)
		paramsTxt_C  += ',' + pTypeName + ' ' + p.name
		paramsTxt_FP += ',' + pTypeName

	#C
	header += retTypeTxt + ' ' + f.name + '(' + paramsTxt_C[1:] + ')'

	#ext
	if f.ext:
		header = "extern " + header

	#int
	else:

		#fp
		if f.isPub:
			zCtx.cpl.resFP   += 'f' + f.name + '\t' + retTypeTxt + paramsTxt_FP + '\n'
			zCtx.cpl.resFP_C += header + ";\n" #<<<<<<<<<<<<<<<<<<< TMP

		#prv
		else:
			header = "static " + header
	zCtx.dbg0("Unparsed FCT HEADER.")
	return header






# -------- MAIN UNPARSE --------

#exe
def unparseExe(zCtx, e, depth, begEnd=True):
	if e.id == ATM__ASG:
		unparseAsg(zCtx, e.dat, depth, begEnd=begEnd)
	elif e.id == ATM__STM_IF:
		unparseStmIf(zCtx, e.dat, depth, begEnd=begEnd)
	elif e.id == ATM__STM_WHI:
		unparseStmWhi(zCtx, e.dat, depth, begEnd=begEnd)
	elif e.id == ATM__STM_SWI:
		unparseStmSwi(zCtx, e.dat, depth, begEnd=begEnd)
	elif e.id == ATM__JMP:
		unparseJmp(zCtx, e.dat, depth, begEnd=begEnd)
	elif e.id == ATM__CALL:
		unparseCall(zCtx, e.dat, depth, begEnd=begEnd)

	#unknown exe
	else:
		zCtx.int("Unknown ID " + str(e.id) + " in exe.", prtSubCtxs=False, prtLine=False)

#scope
def unparseScope(zCtx, scope, depth=1, skipFirstDIs=0):
	for di in scope.datItms:
		if skipFirstDIs != 0:
			skipFirstDIs -= 1
		else:
			unparseDatDcl(zCtx, di, depth)
	for e in scope.header:
		unparseExe(zCtx, e, depth)
	for e in scope.exes:
		unparseExe(zCtx, e, depth)
	for e in scope.footer:
		unparseExe(zCtx, e, depth)






# -------- EXECUTION --------

#main
def c08_unparseAsC(zCtx):
	zCtx.updateLogLvl(STEP.C08)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================== C08 UNPARSE AS C : beginning =========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	# <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TMP
	zCtx.cpl.resC += "typedef   signed char      GUbol;\n"
	zCtx.cpl.resC += "typedef   signed char      GUs8;\n"
	zCtx.cpl.resC += "typedef unsigned char      GUu8;\n"
	zCtx.cpl.resC += "typedef   signed short     GUs16;\n"
	zCtx.cpl.resC += "typedef unsigned short     GUu16;\n"
	zCtx.cpl.resC += "typedef   signed int       GUs32;\n"
	zCtx.cpl.resC += "typedef unsigned int       GUu32;\n"
	zCtx.cpl.resC += "typedef   signed long long GUs64;\n"
	zCtx.cpl.resC += "typedef unsigned long long GUu64;\n"
	zCtx.cpl.resC += "typedef float              GUf32;\n"
	zCtx.cpl.resC += "typedef long double        GUf64;\n"
	zCtx.cpl.resC += "typedef void*              GUref;\n"
	#zCtx.cpl.resC += "static w(GUref src, GUref dst, GUs64 len) {\n"
	#zCtx.cpl.resC += RES__OUTPUT_TAB + "for(GUsmax i=0; i < len; i++){ ((GUs8*)dst)[i] = ((GUs8*)src)[i]; }\n"
	#zCtx.cpl.resC += "}\n"

	#types
	for tID in range(len(zCtx.cpl.types)):
		unparseType(zCtx, tID)

	#gbl scope
	unparseScope(zCtx, zCtx.cpl.gblScp, depth=0)

	#for each compilable fct (int/ext, everything except dcn-dep)
	fctHeaders = {} #map[fct,str]
	for f in zCtx.cpl.fcts:
		if f.content is None:

			#get only header for the moment (to get rid of any calling dependency)
			h             = unparseFctHeader(zCtx, f)
			fctHeaders[f] = h
			zCtx.cpl.resC += h + ";\n"

	#unparse fcts content now
	for f in zCtx.cpl.fcts:
		if f.content is None:
			if not f.ext:
				zCtx.cpl.resC += fctHeaders[f] + " {\n"
				unparseScope(zCtx, f.scope, skipFirstDIs=len(f.params))
				zCtx.cpl.resC += "}\n"

	#final msg if everything went OK, still cool to have that info
	zCtx.dbg0("Types ID table: " + zCtx.listTypeNames())

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================== C08 UNPARSE AS C : end =========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

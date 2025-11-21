#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- SPECIFIC UNPARSE --------

#value
def unparseVal(zCtx, v, depth, casht=True):
	zCtx.dbg0("Unparsing VAL " + v.toStr(depth=1), prtSubCtxs=False, prtLine=False)

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< MAYBE KEEP THIS...
	casht = False

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

	#unknown
	else:
		zCtx.int("Unknown ID " + str(v.vdat.id) + " in value.", prtSubCtxs=False, prtLine=False)

	#end
	if casht:
		zCtx.cpl.resC += ')'
	zCtx.dbg0("Unparsed VAL.", prtSubCtxs=False, prtLine=False)



#datItm
def unparseDatDcl(zCtx, di, depth, begEnd=True):
	zCtx.dbg0("Unparsing DAT DCL " + di.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d   = TERM__OUTPUT_TAB * depth
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
				zCtx.cpl.resFP_C += dcl #<<<<<<<<<<<<<<<<<<< TMP

			#prv
			else:
				zCtx.cpl.resC += "static "

		#both gbl & lcl
		zCtx.cpl.resC += dcl

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed DAT DCL.", prtSubCtxs=False, prtLine=False)



#asg
def unparseAsg(zCtx, a, depth, begEnd=True):
	zCtx.dbg0("Unparsing ASG " + a.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#"name = val;"
	unparseVal(zCtx, a.dst, depth, casht=False)
	zCtx.cpl.resC += " = "
	unparseVal(zCtx, a.src, depth, casht=False)

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed ASG.", prtSubCtxs=False, prtLine=False)



#stm if
def unparseStmIf(zCtx, i, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"if(cond){scp}else if(cond){scp}else{scp}"
	zCtx.dbg0("Unparsing IF " + i.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#conditional blocks
	c = 0
	while c < len(i.conds):
		zCtx.cpl.resC += "if("
		unparseVal(zCtx, i.conds[c], depth+1)
		zCtx.cpl.resC += "){\n"
		unparseScope(zCtx, i.scopes[c], depth=depth+1)
		zCtx.cpl.resC += d + "}el"
		c += 1

	#els block
	if len(i.scopes) > len(i.conds):
		zCtx.cpl.resC += "se{\n"
		unparseScope(zCtx, i.scopes[c], depth=depth+1)
		zCtx.cpl.resC += d + "}\n"
	else:
		zCtx.cpl.resC = str_sub(zCtx.cpl.resC, stop=-3) + '\n'
	zCtx.dbg0("Unparsed IF.", prtSubCtxs=False, prtLine=False)



#for
def unparseStmFor(zCtx, f, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"for(iterDIType iterDIName=iterDIInitVal; iterCond; iterOpe){scp}"
	zCtx.dbg0("Unparsing FOR " + f.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d
	zCtx.cpl.resC += "for("

	#iterDI
	iterDITypeName = zCtx.getTypeNameFromID(f.iterDatItm.Type)
	zCtx.cpl.resC += iterDITypeName + ' ' + f.iterDatItm.name + '='
	unparseVal(zCtx, f.iterDatItm.initVal, depth+1)
	zCtx.cpl.resC += ';'

	#iterCond
	unparseVal(zCtx, f.iterCond, depth+1)
	zCtx.cpl.resC += ';'

	#iterExe
	unparseExe(zCtx, f.iterExe, depth+1, begEnd=False)
	zCtx.cpl.resC += "){\n"

	#scope
	unparseScope(zCtx, f.scope, depth=depth+1)
	zCtx.cpl.resC += d + "}\n"
	zCtx.dbg0("Unparsed FOR.", prtSubCtxs=False, prtLine=False)



#whi
def unparseStmWhi(zCtx, w, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"while(cond){scp}"
	zCtx.dbg0("Unparsing WHI " + w.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

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
	zCtx.dbg0("Unparsed WHI.", prtSubCtxs=False, prtLine=False)



#swi
def unparseStmSwi(zCtx, s, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"switch(){case c1val:{scp} c2val:{scp} def:{}}"
	zCtx.dbg0("Unparsing SWI " + s.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d   = TERM__OUTPUT_TAB * depth
	dp1 = d + TERM__OUTPUT_TAB

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
	zCtx.dbg0("Unparsed SWI.", prtSubCtxs=False, prtLine=False)



#jmp
def unparseJmp(zCtx, j, depth, begEnd=True):
	if depth == 0:
		sbj.int("Got JMP in gbl scp.", prtSubCtxs=False, prtLine=False)

	#"break;", "continue;", "return ;", "return val;"
	zCtx.dbg0("Unparsing JMP " + j.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

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
			unparseVal(zCtx, j.retVal, depth, casht=False)

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed JMP.", prtSubCtxs=False, prtLine=False)



#call
def unparseCall(zCtx, c, depth, begEnd=True):

	#"name(p1,p2...);"
	zCtx.dbg0("Unparsing CALL " + c.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#beg mark (shift)
	if begEnd:
		zCtx.cpl.resC += d

	#name
	zCtx.cpl.resC += c.name + "(\n"

	#params
	for p in c.paramVals:
		zCtx.cpl.resC += d + TERM__OUTPUT_TAB
		unparseVal(zCtx, p, depth+1)
		zCtx.cpl.resC += ",\n"
	zCtx.cpl.resC = str_sub(zCtx.cpl.resC, stop=-3) + '\n' #immutable str in python, but in Z, we can simply make resC[-2] = ' ' <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	zCtx.cpl.resC += d + ")"

	#end mark
	if begEnd:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed CALL.", prtSubCtxs=False, prtLine=False)



#fct
def unparseFctHeader(zCtx, f):
	zCtx.dbg0("Unparsing FCT HEADER of " + f.toStr(depth=1), prtSubCtxs=False, prtLine=False)
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
		zCtx.cpl.resC += "extern " + header + ";\n"

	#int
	else:

		#fp
		if f.isPub:
			zCtx.cpl.resFP   += 'f' + f.name + '\t' + retTypeTxt + paramsTxt_FP + '\n'
			zCtx.cpl.resFP_C += header + ";\n" #<<<<<<<<<<<<<<<<<<< TMP

		#prv
		else:
			zCtx.cpl.resC += "static "

		#C
		zCtx.cpl.resC += header + " {\n"
	zCtx.dbg0("Unparsed FCT HEADER.", prtSubCtxs=False, prtLine=False)






# -------- MAIN UNPARSE --------

#exe
def unparseExe(zCtx, e, depth, begEnd=True):
	if e.id == ATM__ASG:
		unparseAsg(zCtx, e.dat, depth, begEnd=begEnd)
	elif e.id == ATM__STM_IF:
		unparseStmIf(zCtx, e.dat, depth, begEnd=begEnd)
	elif e.id == ATM__STM_FOR:
		unparseStmFor(zCtx, e.dat, depth, begEnd=begEnd)
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
def unparseScope(zCtx, scope, depth=1):
	for di in scope.datItms:
		unparseDatDcl(zCtx, di, depth)
	for e in scope.exes:
		unparseExe(zCtx, e, depth)






# -------- EXECUTION --------

#main
def c04_unparseAsC(zCtx):
	zCtx.updateLogLvl(STEP.C04)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================== C04 UNPARSE AS C : beginning =========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#gbl scope
	unparseScope(zCtx, zCtx.cpl.gblScp, depth=0)

	#unparse every function that has been compiled
	for f in zCtx.cpl.fcts:
		if f.content is None: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< EUUUUUUUUUUUUUUUUU
			#zCtx.cpl.resC += "\n\n\nF \"" + f.name + "\"\n\n"
			unparseFctHeader(zCtx, f)
			#zCtx.cpl.resC += "F \"" + f.name + "\" SCOPE\n\n"
			unparseScope(zCtx, f.scope)
			if not f.ext:
				zCtx.cpl.resC += "}\n"

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================== C04 UNPARSE AS C : end =========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	#if log_lvl[0] >= LOG__LVL_DBG0:
	#	prepareDbgDir()
	#	writeFIle("dbg/" + ..., ...) <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< NOTHING I GUESS...

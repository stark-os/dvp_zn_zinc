#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- SPECIFIC UNPARSE --------

#value
def unparseVal(zCtx, v, depth):
	zCtx.dbg0("Unparsing VAL " + v.toStr(depth=1), prtSubCtxs=False, prtLine=False)

	#cast res
	zCtx.cpl.resC += "(" + zCtx.getTypeNameFromID(v.Type) + ")("

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
		unparseCall(zCtx, v.vdat.dat, depth, VFC=False)

	#unknown
	else:
		zCtx.int("Unknown ID " + str(v.vdat.id) + " in value.", prtSubCtxs=False, prtLine=False)

	#end
	zCtx.cpl.resC += ")"
	zCtx.dbg0("Unparsed VAL.", prtSubCtxs=False, prtLine=False)



#datItm
def unparseDatDcl(zCtx, di, depth):
	zCtx.dbg0("Unparsing DAT DCL " + di.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d   = TERM__OUTPUT_TAB * depth
	dcl = ""

	#"type name;"
	if depth == 0 and not di.isPub: #0 depth <=> gbl
		dcl += "static "
	if di.Cst:
		dcl += "const "
	dcl += zCtx.getTypeNameFromID(di.Type) + ' ' + di.name + ";\n"

	#res
	zCtx.cpl.resC += d + dcl

	#fp
	if depth == 0 and di.isPub:
		zCtx.cpl.resFP += dcl + ";\n"
		zCtx.cpl.resFP_C += dcl + ";\n" #<<<<<<<<<<<<<<<<<<< TMP
	zCtx.dbg0("Unparsed DAT DCL.", prtSubCtxs=False, prtLine=False)



#asg
def unparseAsg(zCtx, a, depth):
	zCtx.dbg0("Unparsing ASG " + a.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"name = val;"
	zCtx.cpl.resC += d
	unparseVal(zCtx, a.dst, depth)
	zCtx.cpl.resC += " = "
	unparseVal(zCtx, a.src, depth)
	zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed ASG.", prtSubCtxs=False, prtLine=False)



#stm if
def unparseStmIf(zCtx, i, depth):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#beginning
	zCtx.dbg0("Unparsing IF " + i.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"if(cond){scp}else if(cond){scp}else{scp}"
	zCtx.cpl.resC += d + "if(){"
	zCtx.cpl.resC += "}\n"
	zCtx.dbg0("Unparsed IF.", prtSubCtxs=False, prtLine=False)



#for
def unparseStmFor(zCtx, f, depth):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#beginning
	zCtx.dbg0("Unparsing FOR " + f.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"for(iterDIType iterDIName=iterDIInitVal; iterCond; iterOpe){scp}"
	zCtx.cpl.resC += d + "for(){"
	zCtx.cpl.resC += "}\n"
	zCtx.dbg0("Unparsed FOR.", prtSubCtxs=False, prtLine=False)



#whi
def unparseStmWhi(zCtx, w, depth):
	if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#beginning
	zCtx.dbg0("Unparsing WHI " + w.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"while(cond){scp}"
	zCtx.cpl.resC += d + "while(){"
	zCtx.cpl.resC += "}\n"
	zCtx.dbg0("Unparsed WHI.", prtSubCtxs=False, prtLine=False)



#swi
def unparseStmSwi(zCtx, s, depth):
	if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)

	#beginning
	zCtx.dbg0("Unparsing SWI " + s.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"switch(){case c1val:{scp} c2val:{scp} def:{}}"
	zCtx.cpl.resC += d + "switch(){\n"
	zCtx.cpl.resC += d + "}\n"
	zCtx.dbg0("Unparsed SWI.", prtSubCtxs=False, prtLine=False)



#jmp
def unparseJmp(zCtx, j, depth):
	if depth == 0:
		sbj.int("Got JMP in gbl scp.", prtSubCtxs=False, prtLine=False)

	#beginning
	zCtx.dbg0("Unparsing JMP " + j.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"break;", "continue;", "return val;"
	if j.kind == JMP__BRK:
		zCtx.cpl.resC += d + "break"
	if j.kind == JMP__CTN:
		zCtx.cpl.resC += d + "continue"
	if j.kind == JMP__RET:
		zCtx.cpl.resC += d + "return "
		unparseVal(zCtx, j.retVal, depth)
	zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed JMP.", prtSubCtxs=False, prtLine=False)



#call
def unparseCall(zCtx, c, depth, VFC=True):
	zCtx.dbg0("Unparsing CALL " + c.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#shift at start
	if VFC:
		zCtx.cpl.resC += d

	#"name(p1,p2...);"
	zCtx.cpl.resC += c.name + "(\n"
	for p in c.paramVals:
		zCtx.cpl.resC += d + TERM__OUTPUT_TAB
		unparseVal(zCtx, p, depth+1)
		zCtx.cpl.resC += ",\n"

	#end
	zCtx.cpl.resC += d + ")"
	if VFC:
		zCtx.cpl.resC += ";\n"
	zCtx.dbg0("Unparsed CALL.", prtSubCtxs=False, prtLine=False)



#fct
def unparseFctHeader(zCtx, f):
	zCtx.dbg0("Unparsing FCT HEADER of " + f.toStr(depth=1), prtSubCtxs=False, prtLine=False)
	header = ""

	#retType
	if f.retType == TYPE_ID__UNKNOWN:
		header += "void"
	else:
		header += zCtx.getTypeNameFromID(f.retType)

	#"retType name(p1type p1name, ...) {"
	params = ""
	for p in f.params:
		params += zCtx.getTypeNameFromID(p.Type) + ' ' + p.name + ","
	header += ' ' + f.name + '(' + params[:-1] + ')'

	#fp
	if f.isPub and not f.ext:
		zCtx.cpl.resFP += header + ";\n"
		zCtx.cpl.resFP_C += header + ";\n" #<<<<<<<<<<<<<<<<<<< TMP

	#ext
	if f.ext:
		zCtx.cpl.resC += "extern " + header + ";\n"

	#int
	else:
		if not f.isPub:
			zCtx.cpl.resC += "static "
		zCtx.cpl.resC += header + " {\n"
	zCtx.dbg0("Unparsed FCT HEADER.", prtSubCtxs=False, prtLine=False)






# -------- MAIN UNPARSE --------

#scope
def unparseScope(zCtx, scope, depth=1):

	#datItm
	for di in scope.datItms:
		unparseDatDcl(zCtx, di, depth)

	#exes
	for e in scope.exes:
		if e.id == ATM__ASG:
			unparseAsg(zCtx, e.dat, depth)
		elif e.id == ATM__STM_IF:
			unparseStmIf(zCtx, e.dat, depth)
		elif e.id == ATM__STM_FOR:
			unparseStmFor(zCtx, e.dat, depth)
		elif e.id == ATM__STM_WHI:
			unparseStmWhi(zCtx, e.dat, depth)
		elif e.id == ATM__STM_SWI:
			unparseStmSwi(zCtx, e.dat, depth)
		elif e.id == ATM__JMP:
			unparseJmp(zCtx, e.dat, depth)
		elif e.id == ATM__CALL:
			unparseCall(zCtx, e.dat, depth)

		#unknown exe
		else:
			zCtx.int("Unknown ID " + str(e.id) + " in exe.", prtSubCtxs=False, prtLine=False)






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

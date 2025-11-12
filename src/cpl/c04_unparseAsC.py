#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- SPECIFIC UNPARSE --------

#value
def unparseVal(zCtx, v, depth):
	d = TERM__OUTPUT_TAB * depth

	#"val"
	zCtx.cpl.resC += d + "VALUE"
	zCtx.cpl.resC += ";\n"



#datItm
def unparseDatItm(zCtx, di, depth):
	d   = TERM__OUTPUT_TAB * depth
	dcl = ""

	#"type name;"
	if depth == 0 and not di.isPub: #0 depth <=> gbl
		dcl += "static "
	if di.Cst:
		dcl += "const "
	dcl += zCtx.getTypeNameFromID(di.Type) + ' ' + di.name + ";\n"

	#res
	zCtx.cpl.resC += dcl

	#fp
	if depth == 0 and isPub:
		zCtx.cpl.resFP += dcl + ";\n"
		zCtx.cpl.resFP_C += dcl + ";\n" #<<<<<<<<<<<<<<<<<<< TMP



#asg
def unparseAsg(zCtx, a, depth):
	d = TERM__OUTPUT_TAB * depth

	#"name = val;"
	zCtx.cpl.resC += d + a.dstDI.name + ' '
	unparseVal(zCtx, a.src, depth)
	zCtx.cpl.resC += ";\n"



#stm if
def unparseStmIf(zCtx, i, depth):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"if(cond){scp}else if(cond){scp}else{scp}"
	zCtx.cpl.resC += d + "if(){"
	zCtx.cpl.resC += "}\n"



#for
def unparseStmFor(zCtx, f, depth):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"for(iterDIType iterDIName=iterDIInitVal; iterCond; iterOpe){scp}"
	zCtx.cpl.resC += d + "for(){"
	zCtx.cpl.resC += "}\n"



#whi
def unparseStm(zCtx, i, depth):
	if depth == 0:
		sbj.int("Got IF STM in gbl scp.", prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"while(cond){scp}"
	zCtx.cpl.resC += d + "while(){"
	zCtx.cpl.resC += "}\n"



#swi
def unparseStmSwi(zCtx, s, depth):
	if depth == 0:
		sbj.int("Got SWI STM in gbl scp.", prtSubCtxs=False, prtLine=False)
	d = TERM__OUTPUT_TAB * depth

	#"switch(){case c1val:{scp} c2val:{scp} def:{}}"
	zCtx.cpl.resC += d + "switch(){"
	zCtx.cpl.resC += "}\n"



#jmp
def unparseJmp(zCtx, j, depth):
	if depth == 0:
		sbj.int("Got JMP in gbl scp.", prtSubCtxs=False, prtLine=False)
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



#fct
def unparseFctHeader(zCtx, f):
	header = ""

	#pub/prv
	if not isPub:
		header += "static "

	#retType
	if f.retType == TYPE_ID__UNKNOWN:
		header += "void"
	else:
		header += zCtx.getTypeNameFromID(f.retType)

	#"retType name(p1type p1name, ...) {"
	header += ' ' + f.name + '('
	for p in f.params:
		header += zCtx.getTypeNameFromID(f.retType) + ' ' + p.name + ", "
	header += ')'
	zCtx.cpl.resC  += header + " {\n"

	#fp
	if isPub:
		zCtx.cpl.resFP += header + ";\n"
		zCtx.cpl.resFP_C += header + ";\n" #<<<<<<<<<<<<<<<<<<< TMP






# -------- MAIN UNPARSE --------

#scope
def unparseScope(zCtx, depth=1):

	#datItm
	for di in zCtx.cpl.gblScp.datItms:
		unparseDatItm(zCtx, di, depth)

	#exes
	for e in zCtx.cpl.gblScp.exes:
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

		#unknown exe
		else:
			zCtx.int("Unknown exe with ID " + e.id, prtSubCtxs=False, prtLine=False)






# -------- EXECUTION --------

#main
def c04_unparseAsC(zCtx):
	zCtx.step = STEP.C04
	zCtx.dbgSepLine()
	zCtx.dbg("=================================================================================")
	zCtx.dbg("========================== C04 UNPARSE AS C : beginning =========================")
	zCtx.dbg("=================================================================================")
	zCtx.deepDbgPause()

	#gbl scope
	unparseScope(zCtx, zCtx.cpl.gblScp, depth=0)

	#unparse every function that has been compiled
	for f in zCtx.cpl.fcts:
		if f.content is None: #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< EUUUUUUUUUUUUUUUUU
			unparseFctHeader(zCtx, f)
			unparseScope(zCtx, f.scope)
			zCtx.cpl.resC += "}\n"

	#debug
	zCtx.dbg("===========================================================================")
	zCtx.dbg("========================== C04 UNPARSE AS C : end =========================")
	zCtx.dbg("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.deepDbgPause()

	#debug output file
	if zCtx.dbgMode[zCtx.step]:
		prepareDbgDir()
		#writeFIle("dbg/" + ..., ...)

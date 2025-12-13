#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- LIST CALLED FCTS --------

#tiny tool
def addCallNameIfValIsCall(calledFcts, v):
	if v.vdat.id == ATM__CALL:
		callName = v.vdat.dat.name
		if callName not in calledFcts:
			calledFcts.append(callName)



#recursively list every fct called
def listCalled(calledFcts, scope):

	#datItms
	for di in scope.datItms:
		if di.inited:
			addCallNameIfValIsCall(calledFcts, di.initVal)

	#exes
	for x in scope.exes:

		#asg
		if x.id == ATM__ASG:
			addCallNameIfValIsCall(calledFcts, x.dat.src)
			addCallNameIfValIsCall(calledFcts, x.dat.dst)

		#if
		elif x.id == ATM__STM_IF:
			addCallNameIfValIsCall(calledFcts, x.dat.cond)
			if x.dat.elsScope is not None:
				listCalled(calledFcts, x.dat.elsScope)

		#whi
		elif x.id == ATM__STM_WHI:
			addCallNameIfValIsCall(calledFcts, x.dat.iterCond)
			listCalled(calledFcts, x.dat.scope)

		#swi
		elif x.id == ATM__STM_SWI:
			addCallNameIfValIsCall(calledFcts, x.dat.tgt)
			for c in x.dat.cases:
				addCallNameIfValIsCall(calledFcts, c)
			for ss in x.dat.scopes:
				listCalled(calledFcts, ss)

		#jmp
		elif x.id == ATM__JMP:
			if x.dat.retVal is not None:
				addCallNameIfValIsCall(calledFcts, x.dat.retVal)

		#call
		elif x.id == ATM__CALL:
			if x.dat.name not in calledFcts:
				calledFcts.append(x.dat.name)






# -------- EXECUTION --------

#main
def c06_unusedFcts(zCtx):
	zCtx.updateLogLvl(STEP.C06)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("========================== C06 UNUSED FCTS : beginning ==========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#list all fct called in the whole program
	calledFcts = [] #lst[str]
	listCalled(calledFcts, zCtx.cpl.gblScp)
	for f in zCtx.cpl.fcts:
		listCalled(calledFcts, f.scope)

	#list every useless fct
	popLst     = [] #lst[smax]
	rmFctNames = [] #lst[str]
	for f in range(len(zCtx.cpl.fcts)):
		fName = zCtx.cpl.fcts[f].name
		if fName not in calledFcts:
			zCtx.dbg0("Function \"" + fName + "\" is never called in program => removing it from result.")
			popLst.append(f)

			#dbg
			rmFctNames.append(fName)

	#rm them (popLst is in asc order, no idx shift to operate)
	for i in popLst:
		zCtx.cpl.fcts = lst_remove(zCtx.cpl.fcts, i)

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================== C06 UNUSED FCTS : end ==========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#sum up
		output = \
			"FCTS REMAINING (used):\n\n" + '\n'.join(calledFcts) + \
			"\n\n\n\nFCTS REMOVED (unused):\n\n" + '\n'.join(rmFctNames) + '\n'
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c06.lst", output)

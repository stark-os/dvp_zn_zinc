#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- DCP BIG VAL AS REF --------

#for each call found, dcp big params as ref
def dcpBigParamAsRef(zCtx, v, scope, idx):
	shift = 0
	if v.vdat.id == ATM__CALL:
		c = v.vdat.dat

		#for each param
		for p in range(len(c.paramVals)):
			p    = len(c.paramVals)-1-p #reverse order to have 1st dcp exe on top (allow potential dep use between each field)
			pVal = c.paramVals[p]

			#big param => to dcp as ref
			if zCtx.getTypeInstanceFromID(pVal.Type).dcnCommon.size > zCtx.smaxSize:
				zCtx.dbg0("Decomposing AS REF, big val in param " + str(p+1) + " of call " + c.name + "() :" + pVal.toStr())

				#dcp DI
				dcpDI     = scope.nxtDcpDatItm(pVal.Type)
				dcpDI_val = val(pVal.Type, atm(ATM__DATITM, dcpDI), False)

				#param contains now a REF to the dcpDI
				c.paramVals[p] = val(zCtx.refType, atm(ATM__FRF, frf(dcpDI)), False)

				#the dcpDI contains the val
				lst_insertBefore(scope.exes, idx, atm(
					ATM__ASG,
					asg(pVal, dcpDI_val)
				))
				zCtx.dbg1("\nScope after dcp: " + scope.toStr())
				shift += 1
				zCtx.dbg0("Decomposed AS REF, big val in param " + str(p+1) + " of call " + c.name + "().")

	#forward as many as we added exes before cur idx
	return shift






# -------- EXECUTION --------

#main
def c07_bigParamAsRef(zCtx):
	zCtx.updateLogLvl(STEP.C07)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("======================== C07 BIG PARAM AS REF : beginning =======================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()



	#STEP 1: DCP BIG PARAM VALS IN CALLS

	#gather every easily accessible scopes
	scopes = [zCtx.cpl.gblScp]
	for f in zCtx.cpl.fcts:
		scopes.append(f.scope)

	#for each scope (flexible iteration)
	s = 0
	while True:
		if s >= len(scopes):
			break
		scope = scopes[s]
		zCtx.dbg2("Entering new scope " + scope.toStr())

		#should no longer have inited value <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< MAYBE RM THIS ONE DAY
		for di in scope.datItms:
			if di.inited:
				zCtx.int("Still having inited datItm after dcpSubVals CPL step.", prtSubCtxs=False, prtLine=False)

		#for each exe (flexible iteration)
		e = 0
		while True:
			if e >= len(scope.exes):
				break
			x = scope.exes[e]
			zCtx.dbg2("Analyzing exe " + x.toStr() + "\n from scope " + scope.toStr())

			#asg
			if x.id == ATM__ASG:
				e += dcpBigParamAsRef(zCtx, x.dat.src, scope, e)
				e += dcpBigParamAsRef(zCtx, x.dat.dst, scope, e)

			#if
			elif x.id == ATM__STM_IF:
				e += dcpBigParamAsRef(zCtx, x.dat.cond, scope, e)
				scopes.append(x.dat.ifScope) #add sub-scope to analyze later
				if x.dat.elsScope is not None:
					scopes.append(x.dat.elsScope) #add sub-scope to analyze later

			#whi
			elif x.id == ATM__STM_WHI:
				e += dcpBigParamAsRef(zCtx, x.dat.iterCond, scope, e)
				scopes.append(x.dat.scope) #add sub-scope to analyze later

			#swi
			elif x.id == ATM__STM_SWI:
				if x.dat.tgt.vdat.id == atmID:
					e += dcpBigParamAsRef(zCtx, x.dat.tgt, scope, e)
				for c in x.dat.cases:
					e += dcpBigParamAsRef(zCtx, c, scope, e)
				for ss in x.dat.scopes:
					scopes.append(ss) #add sub-scope to analyze later

			#jmp
			elif x.id == ATM__JMP:
				if x.dat.retVal is not None:
					e += dcpBigParamAsRef(zCtx, x.dat.retVal, scope, e)

			#call (VFC)
			elif x.id == ATM__CALL:
				v = val(x.dat.retType, atm(ATM__CALL, x.dat), False) #create virtual val just for running dcp on it, this val does not exist in the code actually
				e += dcpBigParamAsRef(zCtx, v, scope, e)

			#obvExe: keep as is
			elif x.id == ATM__OBVEXE:
				pass

			#unknown exe
			else:
				zCtx.int("Unknown EXE with ID " + str(x.id), prtSubCtxs=False, prtLine=False)

			#inc exe idx
			e += 1

		#inc scp idx
		zCtx.dbgPause()
		s += 1



	#STEP 2: TURN BIG PARAMS INTO REF IN FCTS

	'''
	#shortcuts
	r    = zCtx.refType
	r_sz = zCtx.getTypeInstanceFromID(r).dcnCommon.size

	#for each fct
	for f in zCtx.cpl.fcts:
		for p in range(len(f.params)):
			paramSz = zCtx.getTypeInstanceFromID(f.params[p].Type).dcnCommon.size
			if paramSz > r_sz:
				f.params[p].Type = f.params[p]
	'''



	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("======================== C07 BIG PARAM AS REF : end =======================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#gather every scope
		output = zCtx.cpl.gblScp.toStr()
		for f in zCtx.cpl.fcts:
			output += f.scope.toStr()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c07.dl", output)

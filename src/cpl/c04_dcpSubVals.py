#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- VAL DCP --------

#dcp
def dcpSubVal(zCtx, v, scope, idx):
	backshift = 0 #only 0 or 1

	#call with sub val
	if v.vdat.id == ATM__CALL:
		c = v.vdat.dat
		for p in range(len(c.paramVals)):
			p = len(c.paramVals)-1-p #reverse order to have 1st dcp exe on top (allow potential dep use between each field)

			#sub val to dcp found
			subValID = c.paramVals[p].vdat.id
			if subValID == ATM__CALL or subValID == ATM__FFA:
				subV = c.paramVals[p]
				zCtx.dbg0("Decomposing sub val in param " + str(p+1) + " of call " + c.name + "() :" + subV.toStr())

				#dcp DI
				dcpDI     = scope.nxtDcpDatItm(subV.Type)
				dcpDI_val = val(subV.Type, atm(ATM__DATITM, dcpDI), False)

				#param contains now the dcpDI
				c.paramVals[p] = dcpDI_val

				#the dcpDI contains the subVal (still to be analyzed, it can contain another subVal => backshift)
				lst_insertBefore(scope.exes, idx, atm(
					ATM__ASG,
					asg(dcpDI_val, subV)
				))
				zCtx.dbg1("\nScope after dcp: " + scope.toStr())
				backshift = 1
				zCtx.dbg0("Decomposed sub val in param " + str(p+1) + " of call " + c.name + "().")

	#ffa with sub val
	elif v.vdat.id == ATM__FFA:
		f = v.vdat.dat

		#sub val to dcp found
		subValID = f.value.vdat.id
		if subValID == ATM__CALL or subValID == ATM__FFA:
			subV = f.value
			zCtx.dbg0("Decomposing sub val in ffa:" + subV.toStr())

			#dcp DI
			dcpDI     = scope.nxtDcpDatItm(subV.Type)
			dcpDI_val = val(subV.Type, atm(ATM__DATITM, dcpDI), False)

			#ffa contains now the dcpDI
			f.value = dcpDI_val

			#the dcpDI contains the subVal (still to be analyzed, it can contain another subVal => backshift)
			lst_insertBefore(scope.exes, idx, atm(
				ATM__ASG,
				asg(dcpDI_val, subV)
			))
			zCtx.dbg1("\nScope after dcp: " + scope.toStr())
			backshift = 1
			zCtx.dbg0("Decomposed sub val in ffa.")

	#if at least 1 exe has been added before cur idx, cur idx refers to it now => have to parse cur idx again => don't move fwd to nxt exe (compensate with a -1 backshift on cur idx)
	return backshift






# -------- EXECUTION --------

#main
def c04_dcpSubVals(zCtx):
	zCtx.updateLogLvl(STEP.C04)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("=========================== C04 DCP SUB VALS : beginning ========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

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



		#STEP 1: TURN DAT ITMS VALS INTO EXES

		#dcp datItm initVal into DCL_DAT without initVal + ASG_ASG
		asgExes = [] #lst[atm]
		for di in scope.datItms:
			if di.inited:

				#"type di = initVal" => "type di" + "di = initVal"
				asgExes.append(atm(ATM__ASG, asg(
					val(di.Type, atm(ATM__DATITM, di), di.Cst),
					di.initVal
				)))
				di.inited  = False
				di.initVal = None

		#add asg exes IN THE CORRECT ORDER
		scope.exes = asgExes + scope.exes



		#STEP 2: DCP SUBVALS IN EXES

		#for each exe (flexible iteration)
		e = 0
		while True:
			if e >= len(scope.exes):
				break
			x = scope.exes[e]
			zCtx.dbg2("Analyzing exe " + x.toStr() + "\n from scope " + scope.toStr())

			#asg
			if x.id == ATM__ASG:
				e -= dcpSubVal(zCtx, x.dat.src, scope, e)
				e -= dcpSubVal(zCtx, x.dat.dst, scope, e)

			#if
			elif x.id == ATM__STM_IF:
				e -= dcpSubVal(zCtx, x.dat.cond, scope, e)
				scopes.append(x.dat.ifScope) #add sub-scope to analyze later
				if x.dat.elsScope is not None:
					scopes.append(x.dat.elsScope) #add sub-scope to analyze later

			#whi
			elif x.id == ATM__STM_WHI:
				e -= dcpSubVal(zCtx, x.dat.iterCond, scope, e)
				scopes.append(x.dat.scope) #add sub-scope to analyze later

			#swi
			elif x.id == ATM__STM_SWI:
				if x.dat.tgt.vdat.id == atmID:
					e -= dcpSubVal(zCtx, x.dat.tgt, scope, e)
				for c in x.dat.cases:
					e -= dcpSubVal(zCtx, c, scope, e)
				for ss in x.dat.scopes:
					scopes.append(ss) #add sub-scope to analyze later

			#jmp
			elif x.id == ATM__JMP:
				if x.dat.retVal is not None:
					e -= dcpSubVal(zCtx, x.dat.retVal, scope, e)

			#call (VFC)
			elif x.id == ATM__CALL:
				v = val(x.dat.retType, atm(ATM__CALL, x.dat), False) #create virtual val just for running dcp on it, this val does not exist in the code actually
				e -= dcpSubVal(zCtx, v, scope, e)

			#unknown exe
			else:
				zCtx.int("Unknown EXE with ID " + str(x.id), prtSubCtxs=False, prtLine=False)

			#inc exe idx
			e += 1
			zCtx.dbgPause()

		#inc scp idx
		s += 1

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("========================== C04 DCP SUB VALS : end =========================")
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
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c04.dl", output)

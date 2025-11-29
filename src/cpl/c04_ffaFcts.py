#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from zctx import *






# -------- EXECUTION --------

#main
def c04_ffaFcts(zCtx):
	zCtx.updateLogLvl(STEP.C04)
	zCtx.dbgSepLine()
	zCtx.dbg0("=================================================================================")
	zCtx.dbg0("============================ C04 FFA FCTS : beginning ===========================")
	zCtx.dbg0("=================================================================================")
	zCtx.dbgPause()

	#gen ffa fcts <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< DISABLED, RELY ON C COMPILATION
	ffa_fcts = []
	'''
	for fieldTypeID in zCtx.cpl.ffa_fieldTypeIDs:



		# STEP 1: ffa_get
		#
		#We will gen the equivalent Z code (except for fct naming):
		#
		#  prv fct ffa_get_fieldType(ref r, smax offset) fieldType {
		#      fieldType res
		#      w(r$smax+offset, @res, #fieldType)
		#      ret res
		#  }

		#create fct params
		param_r      = datItm(zCtx.refType,  "Lr",      False, None)
		param_offset = datItm(zCtx.smaxType, "Loffset", False, None)
		res          = datItm(fieldTypeID,   "Lres",    False, None)

		#create fct
		f = newFct(
			"ffa_get_" + str(fieldTypeID),
			fieldTypeID,
			[param_r, param_offset],
			zCtx.cpl.gblScp
		)

		#add every datItm
		f.content = None
		f.scope.datItms.append(param_r)
		f.scope.datItms.append(param_offset)
		f.scope.datItms.append(res)

		#compute "r$smax+offset"
		param_r_val      = val(zCtx.smaxType, atm(ATM__DATITM, param_r     ), False)
		param_offset_val = val(zCtx.smaxType, atm(ATM__DATITM, param_offset), False)
		addFct           = zCtx__findMatchingOperator(zCtx,
			"Obad",
			[zCtx.smaxType, zCtx.smaxType],
			["GUsmax",      "GUsmax"]
		)
		if addFct is None:
			zCtx.err(
				"Available combinations for this operator are " + zCtx__listAllExistingOpeNames(zCtx, "Obad") + \
				"\nUnable to find suitable BAD operator between 2 smax => unable to compute very basic \"ffa_get\".",
				prtSubCtxs=False, prtLine=False
			)
		r_plus_offset_val = val(addFct.retType, atm(
			ATM__CALL,
			call(
				addFct.name,
				[param_r_val, param_offset_val],
				addFct.retType
			),
		), False)

		#compute "@res"
		res_val    = val(res.Type, atm(ATM__DATITM, res), False)
		resRef_val = val(zCtx.refType, atm(
			ATM__CALL, call("frf", [res_val], zCtx.refType)
		), False)

		#compute "#fieldType"
		fieldTypeSize_val = val(zCtx.smaxType, atm(
			ATM__U32,
			zCtx.getTypeInstanceFromID(fieldTypeID).dcnCommon.size
		), True)

		#add exes "w(r$smax+offset, @res, #fieldType)"
		f.scope.exes.append(atm(
			ATM__CALL, call(
				"GFw", [
					r_plus_offset_val,
					resRef_val,
					fieldTypeSize_val
				], TYPE_ID__UNKNOWN
			)
		))

		#add "ret res"
		f.scope.exes.append(atm(
			ATM__JMP,
			jmp(JMP__RET, res_val)
		))

		#prv fct => should be optimized to disappear completely after compilation
		f.isPub = False
		ffa_fcts.append(f)



		#STEP 2: ffa_set
		#
		#We will gen the equivalent Z code (except for fct naming):
		#
		#  prv fct ffa_set_fieldType(ref r, smax offset, fieldType v) {
		#      w(@v, r$smax+offset, #fieldType)
		#  }

		#additional fct params
		param_v = datItm(fieldTypeID, "Lv", False, None)

		#create fct
		f = newFct(
			"ffa_set_" + str(fieldTypeID),
			TYPE_ID__UNKNOWN,
			[param_r, param_offset, param_v], #we don't care if they point to the same params as ffa_get, this is OK for compilation purpose
			zCtx.cpl.gblScp
		)

		#add every datItm
		f.content = None
		f.scope.datItms.append(param_r)
		f.scope.datItms.append(param_offset)
		f.scope.datItms.append(param_v)

		#compute "@v"
		param_v_val     = val(param_v.Type, atm(ATM__DATITM, param_v), False)
		param_v_ref_val = val(zCtx.refType, atm(
			ATM__CALL, call("frf", [param_v_val], zCtx.refType)
		), False)

		#add exes "w(@v, r$smax+offset, #fieldType)"
		f.scope.exes.append(atm(
			ATM__CALL, call(
				"GFw", [
					param_v_ref_val,
					r_plus_offset_val,
					fieldTypeSize_val
				], TYPE_ID__UNKNOWN
			)
		))

		#prv fct => should be optimized to disappear completely after compilation
		f.isPub = False
		ffa_fcts.append(f)
	'''


	#add to fcts
	zCtx.cpl.fcts += ffa_fcts

	#debug
	zCtx.dbg0("===========================================================================")
	zCtx.dbg0("============================ C04 FFA FCTS : end ===========================")
	zCtx.dbg0("===========================================================================")
	zCtx.dbgSepLine()
	zCtx.dbgPause()

	#debug output file
	if log_lvl[0] >= LOG__LVL_DBG0:
		prepareDbgDir()

		#get only ffa fcts
		output = ""
		for f in ffa_fcts:
			output += f.toStr()

		#write out current res
		writeFile("dbg/" + path_name(zCtx.initialCtx.filename) + ".c04.dl", output)

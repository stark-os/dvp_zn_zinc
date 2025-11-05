# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/rootStc.py

# ---------------- ROOT STRUCTURES ----------------

#add every root stc + their fcts
'''
def zCtx__addRootStcs(sbj):
	rootStcTypes = [0,0,0]



	# 1ST ROOT STC: TAB

	#create undcn variant
	tID = sbj.cpl.newTyp(
		"GUtab",
		dcnDeg = 1,
		size   = 3*sbj.maxPrmSize # #(ulng lenMax) + #(ulng len) + #(ref dat)
	)
	tInst = sbj.getTypeInstanceFromID(tID)

	#set it as stc
	tInst.dcnCommon.nature = NATURE__STC
	tInst.dcnCommon.fields = [
		datItm(sbj.maxPrmType, "lenMax", False, None          ), #don't let user access to the "dat" field
		datItm(sbj.maxPrmType, "len",    True,  sbj.maxPrmZero)
	]

	#keep track of undcn ID
	rootStcTypes[RST__TAB] = tID



	# 2ND ROOT STC: DLT

	#create undcn variant
	tID = sbj.cpl.newTyp(
		"GUdlt",
		dcnDeg = 1,
		size   = 3*sbj.maxPrmSize # #(ulng lenMax) + #(ulng len) + #(ref dat)
	)
	tInst = sbj.getTypeInstanceFromID(tID)

	#set it as stc
	tInst.dcnCommon.nature = NATURE__STC
	tInst.dcnCommon.fields = [
		datItm(sbj.maxPrmType, "lenMax", False, None          ), #don't let user access to the "dat" field
		datItm(sbj.maxPrmType, "len",    True,  sbj.maxPrmZero)
	]

	#keep track of undcn ID
	rootStcTypes[RST__DLT] = tID



	# 3RD ROOT STC: LST

	#create undcn variant
	tID = sbj.cpl.newTyp(
		"GUlst",
		dcnDeg = 1,
		size   = 2*sbj.maxPrmSize # #(ulng len) + #(ref dat)
	)
	tInst = sbj.getTypeInstanceFromID(tID)

	#set it as stc
	tInst.dcnCommon.nature = NATURE__STC
	tInst.dcnCommon.fields = [
		datItm(sbj.maxPrmType, "len", True, sbj.maxPrmZero) #don't let user access to the "dat" field
	]

	#keep track of undcn ID
	rootStcTypes[RST__LST] = tID
	return rootStcTypes
'''

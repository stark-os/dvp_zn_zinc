# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/type.py

# ABSTRACT ZCEs PARSING TOOLS

#expecting a Z type
def readType(ZCI,
	ZCIKindIfErr,
	errIfNotExisting  = True,
	forbidDcnKw       = True, #toggle possibility to have 'dcn' (=gncDcnType) as type only!
	forbidDcnKwInDcns = True, #toggle possibility to have 'dcn' (=gncDcnType) in dcns only
	dcnKwLstToReplace = None  #toggle possibility to have 'dcn#' (=spcDcnTypes) as type or in dcns
):
	ZCIDeepDbg(ZCI, "Reading type.", prtLine=False)
	initialZCICtx = ZCI.ctx.copy()

	#sub-err indication
	ZCIKindIfErr_forMissingName = None #specific case
	ZCIKindIfErr_ending         = "."
	if ZCIKindIfErr is not None:
		ZCIKindIfErr_ending = ", in " + ZCIKindIfErr

		#specific sub-err case
		if errIfNotExisting:
			ZCIKindIfErr_forMissingName = "Type name in " + ZCIKindIfErr_ending

	#read raw type name (actually, it also includes explicit module prefix if any... so not really "raw")
	tModPfx, tRawName = readName(ZCI, ZCIKindIfErr_forMissingName, parseModPfxes=True)

	#build full type name (forced "undeclinated" for the moment)
	tUndecFullName = tModPfx + 'U' + tRawName



	#1 - check UNDECLINATED variant existence
	tID = ZCI.getTypeIDFromName(tUndecFullName)
	if tID == TYPE_ID__UNKNOWN:

		#case 1: type not found => error
		if errIfNotExisting:
			ZCIWrn(ZCI, "Available types are " + ZCI.zCtx.listTypeNames())
			ZCIErr(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " does not exist" + ZCIKindIfErr_ending)

		#case 2: maybe it was not a type at all
		ZCIDeepDbg(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", prtLine=False)
		ZCI.resetCtx(initialZCICtx)
		ZCIDeepDbg(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
		return TYPE_ID__UNKNOWN



	#2 - dcn / dcn# keywords

	#specific dcn keyword => must be in the specified range
	if dcnKwLstToReplace is not None:
		for t in range(len(ZCI.zCtx.spcDcnTypes)):
			if tID == ZCI.zCtx.spcDcnTypes[t]:

				#too big dcn idx given
				if t > len(dcnKwLstToReplace):
					ZCIErr(ZCI, "Too much degree in \"dcn#\" keyword (" + str(t) + " given, maximum " + str(len(dcnKwLstToReplace)) + " allowed)" + ZCIKindIfErr_ending)

				#replace the original "dcn#" type by the corresponding replacement
				else:
					tID = dcnKwLstToReplace[t]
					break

	#generic dcn keyword
	if tID == ZCI.zCtx.gncDcnType:
		if forbidDcnKw:
			ZCIErr(ZCI, "Generic \"dcn\" keyword is not allowed in type here" + ZCIKindIfErr_ending)

	#got it
	ZCIDeepDbg(ZCI, "Undeclinated type \"" + tUndecFullName + "\" targetted.")



	#3 - declination list given => solve them
	if ZCI.get() == '[':
		initialIdx = ZCI.ctx.icontent.idx
		peerIdx    = ZCI.pairs[initialIdx]
		ZCI.inc()

		#undeclinable type
		tUndecInst = ZCI.getTypeInstanceFromID(tID)
		if tUndecInst.dcnCommon.dcnDeg == 0:
			ZCIErr(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " is not declinable (null declination degree)" + ZCIKindIfErr_ending)

		#read declination types one by one
		ZCIDeepDbg(ZCI, "Type is declinated, reading declination types.", prtLine=False)
		dcns = [] #lst[int]
		while True:
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

			#read dcn type following the given conditions
			dcn = readType(ZCI,
				ZCIKindIfErr,
				forbidDcnKw       = forbidDcnKwInDcns, #dcns of 1st level can be 'dcn', but not in further depth
				dcnKwLstToReplace = dcnKwLstToReplace
			)

			#read & append next declination type (recursive call). Don't check if already exitsing in dcns, we can have the same type twice, thrice and so on...
			dcns.append(dcn)

			#must be followed by coma or closing peer
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
			next = ZCI.get()
			if next == ']':
				if ZCI.ctx.icontent.idx != peerIdx:
					ZCIInt(ZCI, "Ending declination type sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
				ZCI.inc()
				break
			elif next != ',':
				ZCIErr(ZCI, "Invalid element given " + next + " in declination types sequence (expected coma separator ',' or closing bracket ']')" + ZCIKindIfErr_ending)
			ZCI.inc()

		#debug
		ZCIDeepDbg(ZCI, "Found declination types [", prtLine=False)
		for d in dcns:
			ZCIDeepDbg(ZCI, TERM__OUTPUT_TAB + ZCI.getTypeNameFromID(d) + ",", prtLine=False)
		ZCIDeepDbg(ZCI, "].", prtLine=False)

		#get that spc dcn, creating it if needed
		tID = getOrCreateSpcTypeDcn(ZCI, ZCIKindIfErr_ending, tUndecInst, dcns)

	#special case for root stcs
	elif tID in ZCI.zCtx.rootStcTypes:
		ZCIErr(ZCI, "Can't use undeclinated variant of root structures" + ZCIKindIfErr_ending)

	#final result
	ZCIDeepDbg(ZCI, "Ended reading type.")
	return tID



#size match
def paramTypeSizesMustMatch(ZCI, ZCIKindIfErr, paramNbr, type1, type2):
	t1Inst = ZCI.getTypeInstanceFromID(type1)
	t2Inst = ZCI.getTypeInstanceFromID(type2)
	if t1Inst.dcnCommon.size != t2Inst.dcnCommon.size:
		ZCIErr(ZCI, "Incompatible type sizes between type \"" + t1Inst.name + "\" with size " + str(t1Inst.dcnCommon.size) + " as parameter " + str(paramNbr) + " and \"" + t2Inst.name + "\" with size " + str(t2Inst.dcnCommon.size) + ", " + ZCIKindIfErr)




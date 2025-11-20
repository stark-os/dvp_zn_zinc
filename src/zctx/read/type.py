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
	ZCIDbg2(ZCI, "Reading type.", prtLine=False)
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
			ZCIErr(ZCI,
				"Available types are " + ZCI.zCtx.listTypeNames() + \
				"\nType " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " does not exist" + ZCIKindIfErr_ending
			)

		#case 2: maybe it was not a type at all
		ZCIDbg2(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", prtLine=False)
		ZCI.resetCtx(initialZCICtx)
		ZCIDbg2(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
		return TYPE_ID__UNKNOWN



	#2 - permission: dcn keywords, raw, ref

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

	#ref & raw types
	elif ZCI.zCtx.cpl.forbidUseRef:
		if tID == ZCI.zCtx.refType:
			ZCIErr(ZCI, "Use of \"ref\" type is not allowed in current compilation mode" + ZCIKindIfErr_ending)
		if tID == ZCI.zCtx.rawType:
			ZCIErr(ZCI, "Use of \"raw\" type is not allowed in current compilation mode" + ZCIKindIfErr_ending)

	#got it
	ZCIDbg2(ZCI, "Undeclinated type \"" + tUndecFullName + "\" targetted.")



	#3 - declination list given => solve them
	if ZCI.get() == '[':
		ZCI.inc()

		#undeclinable type
		tUndecInst = ZCI.getTypeInstanceFromID(tID)
		if tUndecInst.dcnCommon.dcnDeg == 0:
			ZCIErr(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " is not declinable (null declination degree)" + ZCIKindIfErr_ending)

		#read declination types one by one
		ZCIDbg2(ZCI, "Type is declinated, reading declination types.", prtLine=False)
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
				ZCI.inc()
				break
			elif next != ',':
				ZCIErr(ZCI, "Invalid element given " + next + " in declination types sequence (expected coma separator ',' or closing bracket ']')" + ZCIKindIfErr_ending)
			ZCI.inc()

		#debug
		ZCIDbg2(ZCI, "Found declination types [", prtLine=False)
		for d in dcns:
			ZCIDbg2(ZCI, TERM__OUTPUT_TAB + ZCI.getTypeNameFromID(d) + ",", prtLine=False)
		ZCIDbg2(ZCI, "].", prtLine=False)

		#get that spc dcn, creating it if needed
		tID = getOrCreateSpcTypeDcn(ZCI, ZCIKindIfErr_ending, tUndecInst, dcns)

	#final result
	ZCIDbg2(ZCI, "Ended reading type.")
	return tID

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/type.py

# ABSTRACT ZCEs PARSING TOOLS

#expecting a Z type
def readType(ZCI, ZCIKindIfErr, errIfNotExisting=True):
	ZCIDeepDbg(ZCI, "Reading type.", prtLine=False)
	initialZCICtx = ZCI.ctx.copy()

	#read raw type name (actually, it also includes explicit module prefix if any... so not really "raw")
	ZCIKindIfErr_forMissingName = None
	if errIfNotExisting and ZCIKindIfErr is not None:
		ZCIKindIfErr_forMissingName = "Type name in " + ZCIKindIfErr
	tRawName = readName(ZCI, ZCIKindIfErr_forMissingName, parseModPfxes=True, modPfxes_asHeaderOnly=True)

	#module-realted / global
	if initialZCICtx.get() == '^':
		tModPfx  = extractModPfx(tRawName)               #save its module prefix elsewhere
		tRawName = str_sub(tRawName, start=len(tModPfx)) # + cut it from "rawName" to keep only the REAL RAW NAME
	else:
		tModPfx = "G"

	#build full type name (forced "undeclinated" for the moment)
	tUndecFullName = tModPfx + 'U' + tRawName



	#1 - check UNDECLINATED variant existence
	tID = ZCI.getTypeIDFromName(tUndecFullName)
	if tID == TYPE_ID__UNKNOWN:

		#case 1: type not found => error
		if errIfNotExisting:
			ZCIErr(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " does not exist.")

		#case 2: maybe it was not a type at all
		ZCIDeepDbg(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", prtLine=False)
		ZCI.resetCtx(initialZCICtx)
		ZCIDeepDbg(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
		return TYPE_ID__UNKNOWN

	#got it
	ZCIDeepDbg(ZCI, "Undeclinated type \"" + tUndecFullName + "\" targetted.")



	#2 - declination list given => solve them
	if ZCI.get() == '[':
		initialIdx = ZCI.ctx.icontent.idx
		peerIdx    = ZCI.pairs[initialIdx]
		ZCI.inc()

		#undeclinable type
		tUndecInst = ZCI.getTypeInstanceFromID(tID)
		if tUndecInst.dcnCommon.dcnDeg == 0:
			ZCIErr(ZCI, "Type " + unpfxMod(tModPfx) + tRawName.replace("__", '_') + " is not declinable (null declination degree).")

		#read declination types one by one
		ZCIDeepDbg(ZCI, "Type is declinated, reading declination types.", prtLine=False)
		dcns = [] #lst[int]
		while True:
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

			#read & append next declination type (recursive call). Don't check if already exitsing in dcns, we can have the same type twice, thrice and so on...
			dcns.append(readType(ZCI, ZCIKindIfErr))

			#must be followed by coma or closing peer
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
			next = ZCI.get()
			if next == ']':
				if ZCI.ctx.icontent.idx != peerIdx:
					ZCIInternal(ZCI, "Ending declination type sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
				ZCI.inc()
				break
			elif next != ',':
				ZCIErr(ZCI, "Invalid element given " + next + " in declination types sequence (expected coma separator ',' or closing bracket ']').")
			ZCI.inc()

		#debug
		ZCIDeepDbg(ZCI, "Found declination types [", prtLine=False)
		for d in dcns:
			ZCIDeepDbg(ZCI, TERM__OUTPUT_TAB + ZCI.getTypeNameFromID(d) + ",", prtLine=False)
		ZCIDeepDbg(ZCI, "].", prtLine=False)

		#one declination does not exist => our current type can't exist
		for d in dcns:
			if d == TYPE_ID__UNKNOWN:
				return TYPE_ID__UNKNOWN

		#check declination length
		if len(dcns) < tUndecInst.dcnCommon.dcnDeg:
			ZCIErr(ZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(tUndecInst.dcnCommon.dcnDeg) + " required).")
		elif len(dcns) > tUndecInst.dcnCommon.dcnDeg:
			ZCIErr(ZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(tUndecInst.dcnCommon.dcnDeg) + " required).")

		#re-build full type name including declinations this time (tModulePfx can be set to "G" by the way, same logic as undeclinated types)
		tDecFullName = tModPfx + 'D' + tRawName
		for d in dcns:
			tDecFullName += '_' + ZCI.getTypeNameFromID(d)

		#check for that declination in currently declared types
		tUndecID = tID
		tID      = ZCI.getTypeIDFromName(tDecFullName)

		#not found => create that declination (this new combination must exist)
		if tID == TYPE_ID__UNKNOWN:
			tID           = ZCI.zCtx.cpl.newTyp(tDecFullName, dcnCommon=tUndecInst.dcnCommon) #share the same dcnCommon (affecting the undeclinated instance will affect every declination)
			tDecInst      = ZCI.getTypeInstanceFromID(tID)
			tDecInst.dcns = dcns
			ZCIDbg(ZCI, "First call of declination \"" + tDecFullName + "\" from type \"" + tUndecFullName + "\", adding it.")

	#final result
	ZCIDeepDbg(ZCI, "Ended reading type.")
	return tID









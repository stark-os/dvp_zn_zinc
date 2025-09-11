# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/type.py

# ABSTRACT ZCEs PARSING TOOLS

#expecting a Z type
def readType(ZCI, ZCIKindIfError, errorIfNotExisting=True, allowUnsolved=False):
	ZCIDeepDebug(ZCI, "Reading type.", printLine=False)
	initialZCICtx = ZCI.ctx.copy()

	#read raw type name (actually, it also includes explicit module prefix if any... so not really "raw")
	ZCIKindIfError_forMissingName = None
	if errorIfNotExisting:
		ZCIKindIfError_forMissingName = "Type name in " + ZCIKindIfError
	tRawName = readName(ZCI, ZCIKindIfError_forMissingName, parseModPrefixes=True, modPrefix_asHeaderOnly=True)

	#module-realted / global
	if initialZCICtx.get() == '^':
		tModPrefix = extractModPrefix(tRawName)               #save its module prefix elsewhere
		tRawName   = str_sub(tRawName, start=len(tModPrefix)) # + cut it from "rawName" to keep only the REAL RAW NAME
	else:
		tModPrefix = "G"

	#build full type name (forced "undeclinated" for the moment)
	tUndecFullName = tModPrefix + 'U' + tRawName



	#1 - check UNDECLINATED variant existence
	tID = ZCI.getTypeIDFromName(tUndecFullName)
	if tID == TYPE_ID__NOT_FOUND:

		#case 1: type not found => error
		if errorIfNotExisting:
			ZCIError(ZCI, "Type " + unprefixizeMod(tModPrefix) + tRawName.replace("__", '_') + " does not exist.")

		#case 2: solve it later
		if allowUnsolved:
			return ZCI.zCtx.cpl.addUnsolvedType(ZCI)

		#case 3: maybe it was not a type at all
		ZCIDeepDebug(ZCI, "Type " + unprefixizeMod(tModPrefix) + tRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", printLine=False)
		ZCI.resetCtx(initialZCICtx)
		ZCIDeepDebug(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
		return TYPE_ID__NOT_FOUND

	#got it
	ZCIDeepDebug(ZCI, "Undeclinated type \"" + tUndecFullName + "\" targetted.")



	#2 - declination list given => solve them
	if ZCI.get() == '[':
		initialIdx = ZCI.ctx.icontent.idx
		peerIdx    = ZCI.pairs[initialIdx]
		ZCI.inc()

		#undeclinable type
		tUndecInst = ZCI.getTypeInstanceFromID(tID)
		if tUndecInst.commonDcnData.dcnDeg == 0:
			ZCIError(ZCI, "Type " + unprefixizeMod(tModPrefix) + tRawName.replace("__", '_') + " is not declinable (null declination degree).")

		#read declination types one by one
		ZCIDeepDebug(ZCI, "Type is declinated, reading declination types.", printLine=False)
		dcns = [] #lst[int]
		while True:
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

			#read & append next declination type (recursive call). Don't check if already exitsing in dcns, we can have the same type twice, thrice and so on...
			dcns.append(readType(ZCI, ZCIKindIfError, allowUnsolved=allowUnsolved))

			#must be followed by coma or closing peer
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
			next = ZCI.get()
			if next == ']':
				if ZCI.ctx.icontent.idx != peerIdx:
					ZCIInternal(ZCI, "Ending declination type sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
				ZCI.inc()
				break
			elif next != ',':
				ZCIError(ZCI, "Invalid element given " + next + " in declination types sequence (expected coma separator ',' or closing bracket ']').")
			ZCI.inc()

		#at least one declination type is unsolved => stop here, considering the whole as "unsolved"
		if allowUnsolved:
			for d in dcns:
				if d < 0:
					return ZCI.zCtx.cpl.addUnsolvedType(ZCI)

		#debug
		ZCIDeepDebug(ZCI, "Found declination types [", printLine=False)
		for d in dcns:
			ZCIDeepDebug(ZCI, "\t" + ZCI.getTypeInstanceFromID(d).name + ",", printLine=False)
		ZCIDeepDebug(ZCI, "].", printLine=False)

		#check declination length
		if len(dcns) < tUndecInst.commonDcnData.dcnDeg:
			ZCIError(ZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(tUndecInst.commonDcnData.dcnDeg) + " required).")
		elif len(dcns) > tUndecInst.commonDcnData.dcnDeg:
			ZCIError(ZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(tUndecInst.commonDcnData.dcnDeg) + " required).")

		#re-build full type name including declinations this time (tModulePrefix can be set to "G" by the way, same logic as undeclinated types)
		tDecFullName = tModPrefix + 'D' + tRawName
		for d in dcns:
			tDecFullName += '_' + ZCI.getTypeInstanceFromID(d).name

		#check for that declination in currently declared types
		tUndecID = tID
		tID      = ZCI.getTypeIDFromName(tDecFullName)

		#not found => create that declination (this new combination must exist)
		if tID == TYPE_ID__NOT_FOUND:
			tID           = ZCI.zCtx.cpl.newTyp(tDecFullName, commonDcnData=tUndecInst.commonDcnData) #share the same commonDcnData (affecting the undeclinated instance will affect every declination)
			tDecInst      = ZCI.getTypeInstanceFromID(tID)
			tDecInst.dcns = dcns
			ZCIDebug(ZCI, "First call of declination \"" + tDecFullName + "\" from type \"" + tUndecFullName + "\", adding it.")

	#final result
	ZCIDeepDebug(ZCI, "Ended reading type.")
	return tID









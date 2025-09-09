# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/type.py

# ABSTRACT ZCEs PARSING TOOLS

#expecting a Z type
def readType(ZCI, ZCIKindIfError, nullIfNotExisting=False):
	ZCIDeepDebug(ZCI, "Reading type.")
	initialZCICtx = ZCI.ctx.copy()

	#read raw type name (actually, it also includes explicit module prefix if any... so not really "raw")
	tRawName = readName(ZCI, "Type name in " + ZCIKindIfError, parseModPrefixes=True, modPrefix_asHeaderOnly=True)

	#module-realted / global
	if initialZCICtx.get() == '^':
		tModPrefix = extractModPrefix(tRawName)               #save its module prefix elsewhere
		tRawName   = str_sub(tRawName, start=len(tModPrefix)) # + cut it from "rawName" to keep only the REAL RAW NAME
	else:
		tModPrefix = "G"

	#build full type name (forced "undeclinated" for the moment)
	tFullName = tModPrefix + 'U' + tRawName

	#1 - check UNDECLINATED variant existence
	tInstance = ZCI.zCtx.getType(tFullName)
	if tInstance is None:
		if nullIfNotExisting:
			ZCIDeepDebug(ZCI, "Type " + unprefixizeMod(tModPrefix) + tRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", printLine=False)
			ZCI.resetCtx(initialZCICtx)
			ZCIDeepDebug(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
			return None
		ZCIError(ZCI, "Type " + unprefixizeMod(tModPrefix) + tRawName.replace("__", '_') + " does not exist.")
	ZCIDeepDebug(ZCI, "Undeclinated type \"" + tFullName + "\" targetted.")

	#2 - declination list given => solve them
	if ZCI.get() == '[':
		initialIdx = ZCI.ctx.icontent.idx
		peerIdx    = ZCI.pairs[initialIdx]
		ZCI.inc()

		#undeclinable type
		if tInstance.commonDcnData.dcnDeg == 0:
			ZCIError(ZCI, "Type " + unprefixizeMod(tModPrefix) + tRawName.replace("__", '_') + " is not declinable (null declination degree).")

		#read declination types one by one
		ZCIDeepDebug(ZCI, "Type is declinated, reading declination types.", printLine=False)
		dcns = [] #lst[typ]
		while True:
			optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

			#read & append next declination type (recursive call). Don't check if already exitsing in dcns, we can have the same type twice, thrice and so on...
			dcns.append(readType(ZCI, ZCIKindIfError))

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

		#debug
		ZCIDeepDebug(ZCI, "Found declination types [", printLine=False)
		for d in range(len(dcns)):
			ZCIDeepDebug(ZCI, "\t" + dcns[d].name + ",", printLine=False)
		ZCIDeepDebug(ZCI, "].", printLine=False)

		#check declination length
		if len(dcns) < tInstance.commonDcnData.dcnDeg:
			ZCIError(ZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(tInstance.commonDcnData.dcnDeg) + " required).")
		elif len(dcns) > tInstance.commonDcnData.dcnDeg:
			ZCIError(ZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(tInstance.commonDcnData.dcnDeg) + " required).")

		#re-build full type name including declinations this time (tModulePrefix can be set to "G" by the way, same logic as undeclinated types)
		tFullName = tModPrefix + 'D' + tRawName
		for d in dcns:
			tFullName += '_' + d.name

		#check for that declination in currently declared types
		tUndeclinatedInstance = tInstance
		tInstance             = ZCI.zCtx.getType(tFullName)

		#not found => create that declination (this new combination must exist)
		if tInstance is None:
			tInstance      = newTyp(tFullName, commonDcnData = tUndeclinatedInstance.commonDcnData) #share the same commonDcnData (affecting the undeclinated instance will affect every declination)
			tInstance.dcns = dcns
			ZCIDebug(ZCI, "First call of declination \"" + tInstance.name + "\" from type \"" + tUndeclinatedInstance.name + "\", adding it.")
			ZCI.zCtx.cpl.types.append(tInstance)

	#final result
	ZCIDeepDebug(ZCI, "Ended reading type.")
	return tInstance









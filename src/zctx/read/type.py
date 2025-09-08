# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/read/type.py

	# ABSTRACT ZCEs PARSING TOOLS

	#expecting a Z type
	def readType(self, ZCI, ZCIKindIfError, nullIfNotExisting=False):
		self.ZCIDeepDebug(ZCI, "Reading type.")
		initialZCICtx = ZCI.ctx.copy()

		#read raw type name (actually, it also includes explicit module prefix if any... so not really "raw")
		tRawName = self.readName(ZCI, "Type name in " + ZCIKindIfError, parseModulePrefixes=True, modulePrefix_asHeaderOnly=True)

		#module-realted / global
		if initialZCICtx.get() == '^':
			tModulePrefix = self.splitModulePrefix(tRawName)            #save its module prefix elsewhere
			tRawName      = str_sub(tRawName, start=len(tModulePrefix)) # + cut it from "rawName" to keep only the REAL RAW NAME
		else:
			tModulePrefix = "G"

		#build full type name (forced "undeclinated" for the moment)
		tFullName = tModulePrefix + 'U' + tRawName

		#1 - check UNDECLINATED variant existence
		tInstance = self.getType(tFullName)
		if tInstance is None:
			if nullIfNotExisting:
				self.ZCIDeepDebug(ZCI, "Type " + unprefixizeModule(tModulePrefix) + tRawName.replace("__", '_') + " does not exist, it may not be a type but something else.", printLine=False)
				ZCI.resetCtx(initialZCICtx)
				self.ZCIDeepDebug(ZCI, "Restoring ZCI context to that position => Ended reading Z type.")
				return None
			self.ZCIError(ZCI, "Type " + unprefixizeModule(tModulePrefix) + tRawName.replace("__", '_') + " does not exist.")
		self.ZCIDeepDebug(ZCI, "Undeclinated type \"" + tFullName + "\" targetted.")

		#2 - declination list given => solve them
		if ZCI.get() == '[':
			initialIdx = ZCI.ctx.icontent.idx
			peerIdx    = ZCI.pairs[initialIdx]
			ZCI.inc()

			#undeclinable type
			if tInstance.commonDcnData.dcnDeg == 0:
				self.ZCIError(ZCI, "Type " + unprefixizeModule(tModulePrefix) + tRawName.replace("__", '_') + " is not declinable (null declination degree).")

			#read declination types one by one
			self.deepDebug("Type is declinated, reading declination types.")
			dcns = [] #lst[typ]
			while True:
				self.optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)

				#read & append next declination type (recursive call). Don't check if already exitsing in dcns, we can have the same type twice, thrice and so on...
				dcns.append(self.readType(ZCI, ZCIKindIfError))

				#must be followed by coma or closing peer
				self.optionalBlanks(ZCI, None, blanks=BLANKS_EXTENDED)
				next = ZCI.get()
				if next == ']':
					if ZCI.ctx.icontent.idx != peerIdx:
						self.ZCIInternal(ZCI, "Ending declination type sequence reading with inconsistent peer index (finished at index " + str(ZCI.ctx.icontent.idx) + " instead of targetted " + str(peerIdx) + ").")
					ZCI.inc()
					break
				elif next != ',':
					self.ZCIError(ZCI, "Invalid element given " + next + " in declination types sequence (expected coma separator ',' or closing bracket ']').")
				ZCI.inc()

			#debug
			self.ZCIDeepDebug(ZCI, "Found declination types [", printLine=False)
			for d in range(len(dcns)):
				self.ZCIDeepDebug(ZCI, "\t" + dcns[d].name + ",", printLine=False)
			self.ZCIDeepDebug(ZCI, "].", printLine=False)

			#check declination length
			if len(dcns) < tInstance.commonDcnData.dcnDeg:
				self.ZCIError(ZCI, "Too few types given for declination (" + str(len(dcns)) + " given, " + str(tInstance.commonDcnData.dcnDeg) + " required).")
			elif len(dcns) > tInstance.commonDcnData.dcnDeg:
				self.ZCIError(ZCI, "Too much types given for declination (" + str(len(dcns)) + " given, " + str(tInstance.commonDcnData.dcnDeg) + " required).")

			#re-build full type name including declinations this time (tModulePrefix can be set to "G" by the way, same logic as undeclinated types)
			tFullName = tModulePrefix + 'D' + tRawName
			for d in dcns:
				tFullName += '_' + d.name

			#check for that declination in currently declared types
			tUndeclinatedInstance = tInstance
			tInstance             = self.getType(tFullName)

			#not found => create that declination (this new combination must exist)
			if tInstance is None:
				tInstance      = newTyp(tFullName, commonDcnData = tUndeclinatedInstance.commonDcnData) #share the same commonDcnData (affecting the undeclinated instance will affect every declination)
				tInstance.dcns = dcns
				self.ZCIDebug(ZCI, "First call of declination \"" + tInstance.name + "\" from type \"" + tUndeclinatedInstance.name + "\", adding it.")
				self.cpl.types.append(tInstance)

		#final result
		self.ZCIDeepDebug(ZCI, "Ended reading type.")
		return tInstance






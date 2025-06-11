
	# ZCI OUTPUT (cpl)

	#output after precompilation is closely related to ZCIs, no longer to global subCtxs
	def ZCIInternal(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.internal(msg, printSubCtxs, printLine)

	def ZCIError(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.error(msg, printSubCtxs, printLine)

	def ZCIWarning(self, ZCI, msg, printSubCtxs=True, printLine=True):
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.warning(msg, printSubCtxs, printLine)

	def ZCIDebug(self, ZCI, msg, printSubCtxs=False, printLine=True):
		previousSubCtxs = self.subCtxs
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.debug(msg, printSubCtxs, printLine)
		self.overwriteSubCtxs(previousSubCtxs) #restore previous subctxs (debug must not affect current zCtx)

	def ZCIDeepDebug(self, ZCI, msg, printSubCtxs=False, printLine=True):
		previousSubCtxs = self.subCtxs
		self.overwriteSubCtxs(ZCI.subCtxs)
		self.deepDebug(msg, printSubCtxs, printLine)
		self.overwriteSubCtxs(previousSubCtxs) #restore previous subctxs (debug must not affect current zCtx)
# DEBUG

	#modules
	def debugModules(self):
		unprefixedModules = ""
		for mp in self.cpl.modulePrefixes:
			unprefixedModules += "\n - " + unprefixizeModule(mp)
		self.debug("Available modules are :" + unprefixedModules)

	#cpl steps output
	def cplStep_debugZCIs(self, cplStep):
		if self.debugMode:
			dumpZCIs(self.ZCIs, "debug/" + path_name(self.initialCtx.filename) + ".c" + cplStep + ".json")




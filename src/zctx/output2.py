# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output2.py

# ZCI OUTPUT (cpl)

#output after precompilation is closely related to ZCIs, no longer to global subCtxs
def ZCIInternal(ZCI, msg, printSubCtxs=True, printLine=True):
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.internal(msg, printSubCtxs, printLine)

def ZCIError(ZCI, msg, printSubCtxs=True, printLine=True):
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.error(msg, printSubCtxs, printLine)

def ZCIWarning(ZCI, msg, printSubCtxs=True, printLine=True):
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.warning(msg, printSubCtxs, printLine)

def ZCIDebug(ZCI, msg, printSubCtxs=False, printLine=True):
	previousSubCtxs = ZCI.zCtx.subCtxs
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.debug(msg, printSubCtxs, printLine)
	zCtx__overwriteSubCtxs(ZCI.zCtx, previousSubCtxs) #restore previous subctxs (debug must not affect current zCtx)

def ZCIDeepDebug(ZCI, msg, printSubCtxs=False, printLine=True):
	previousSubCtxs = ZCI.zCtx.subCtxs
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.deepDebug(msg, printSubCtxs, printLine)
	zCtx__overwriteSubCtxs(ZCI.zCtx, previousSubCtxs) #restore previous subctxs (debug must not affect current zCtx)



# DEBUG

#modules
def zCtx__debugMods(zCtx):
	unprefixedMods = ""
	for mp in zCtx.cpl.modPrefixes:
		unprefixedMods += "\n - " + unprefixizeMod(mp)
	zCtx.debug("Available modules are :" + unprefixedMods)

#cpl steps output
def zCtx__cplStep_debugZCIs(zCtx, cplStep):
	if zCtx.debugMode:
		dumpZCIs(zCtx.ZCIs, "debug/" + path_name(zCtx.initialCtx.filename) + ".c" + cplStep + ".dl", oneLine=False)







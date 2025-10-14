# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output2.py

# ZCI OUTPUT (cpl)

#output after precompilation is closely related to ZCIs, no longer to global subCtxs
def ZCIInternal(ZCI, msg, prtSubCtxs=True, prtLine=True):
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.internal(msg, prtSubCtxs, prtLine)

def ZCIErr(ZCI, msg, prtSubCtxs=True, prtLine=True):
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.err(msg, prtSubCtxs, prtLine)

def ZCIWrn(ZCI, msg, prtSubCtxs=True, prtLine=True):
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.wrn(msg, prtSubCtxs, prtLine)

def ZCIDbg(ZCI, msg, prtSubCtxs=False, prtLine=True):
	prevSubCtxs = ZCI.zCtx.subCtxs
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.dbg(msg, prtSubCtxs, prtLine)
	zCtx__overwriteSubCtxs(ZCI.zCtx, prevSubCtxs) #restore previous subctxs (debug must not affect current zCtx)

def ZCIDeepDbg(ZCI, msg, prtSubCtxs=False, prtLine=True):
	prevSubCtxs = ZCI.zCtx.subCtxs
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.deepDbg(msg, prtSubCtxs, prtLine)
	zCtx__overwriteSubCtxs(ZCI.zCtx, prevSubCtxs) #restore previous subctxs (debug must not affect current zCtx)



# DEBUG

#modules
def zCtx__dbgMods(zCtx):
	unpfxMods = ""
	for mp in zCtx.cpl.modPfxs:
		unpfxMods += "\n - " + unpfxMod(mp)
	zCtx.dbg("Available modules are :" + unpfxMods)








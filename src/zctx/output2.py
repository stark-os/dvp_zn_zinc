# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output2.py

# ZCI OUTPUT (cpl)

#output after precompilation is closely related to ZCIs, no longer to global subCtxs
def ZCIInt(ZCI, msg, prtSubCtxs=True, prtLine=True):

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.int(msg, prtSubCtxs, prtLine)



def ZCIErr(ZCI, msg, prtSubCtxs=True, prtLine=True):

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.err(msg, prtSubCtxs, prtLine)



def ZCIWrn(ZCI, msg, prtSubCtxs=True, prtLine=True):

	#keep cur status aside
	curStartIdx = ZCI.startIdx
	curTxt      = ZCI.txt

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.wrn(msg, prtSubCtxs, prtLine)

	#reset cur reading head (potentially shifted)
	ZCI.startIdx = curStartIdx
	ZCI.txt      = curTxt



def ZCIDbg(ZCI, msg, prtSubCtxs=False, prtLine=True):

	#keep cur status aside
	curStartIdx = ZCI.startIdx
	curTxt      = ZCI.txt
	prevSubCtxs = ZCI.zCtx.subCtxs

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.dbg(msg, prtSubCtxs, prtLine)

	#reset cur status (beginning potentially shifted)
	ZCI.startIdx = curStartIdx
	ZCI.txt      = curTxt
	zCtx__overwriteSubCtxs(ZCI.zCtx, prevSubCtxs)



def ZCIDeepDbg(ZCI, msg, prtSubCtxs=False, prtLine=True):

	#keep cur status aside
	curStartIdx = ZCI.startIdx
	curTxt      = ZCI.txt
	prevSubCtxs = ZCI.zCtx.subCtxs

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.deepDbg(msg, prtSubCtxs, prtLine)

	#reset cur status (beginning potentially shifted)
	ZCI.startIdx = curStartIdx
	ZCI.txt      = curTxt
	zCtx__overwriteSubCtxs(ZCI.zCtx, prevSubCtxs)



# DEBUG

#modules
def zCtx__dbgMods(zCtx):
	unpfxMods = ""
	for mp in zCtx.cpl.modPfxs:
		unpfxMods += "\n - " + unpfxMod(mp)
	zCtx.dbg("Available modules are :" + unpfxMods)








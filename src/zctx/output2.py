# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/output2.py

# ZCI OUTPUT (cpl)

#output after precompilation is closely related to ZCIs, no longer to global subCtxs
def ZCIInt(ZCI, msg, prtSubCtxs=True, prtLine=True):

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.int(msg, prtSubCtxs, prtLine)



def ZCIErr(ZCI, msg, prtSubCtxs=True, prtLine=True, err=1):

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.err(msg, prtSubCtxs, prtLine, err=err)



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



def ZCIDbg0(ZCI, msg, prtSubCtxs=False, prtLine=True):

	#keep cur status aside
	curStartIdx = ZCI.startIdx
	curTxt      = ZCI.txt
	prevSubCtxs = ZCI.zCtx.subCtxs

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.dbg0(msg, prtSubCtxs, prtLine)

	#reset cur status (beginning potentially shifted)
	ZCI.startIdx = curStartIdx
	ZCI.txt      = curTxt
	zCtx__overwriteSubCtxs(ZCI.zCtx, prevSubCtxs)



def ZCIDbg1(ZCI, msg, prtSubCtxs=False, prtLine=True):

	#keep cur status aside
	curStartIdx = ZCI.startIdx
	curTxt      = ZCI.txt
	prevSubCtxs = ZCI.zCtx.subCtxs

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.dbg1(msg, prtSubCtxs, prtLine)

	#reset cur status (beginning potentially shifted)
	ZCI.startIdx = curStartIdx
	ZCI.txt      = curTxt
	zCtx__overwriteSubCtxs(ZCI.zCtx, prevSubCtxs)



def ZCIDbg2(ZCI, msg, prtSubCtxs=False, prtLine=True):

	#keep cur status aside
	curStartIdx = ZCI.startIdx
	curTxt      = ZCI.txt
	prevSubCtxs = ZCI.zCtx.subCtxs

	#log as original file dat
	zCtx__overwriteSubCtxs(ZCI.zCtx, ZCI.subCtxs)
	ZCI.zCtx.dbg2(msg, prtSubCtxs, prtLine)

	#reset cur status (beginning potentially shifted)
	ZCI.startIdx = curStartIdx
	ZCI.txt      = curTxt
	zCtx__overwriteSubCtxs(ZCI.zCtx, prevSubCtxs)



# DEBUG

#modules
def zCtx__dbgMods(zCtx):
	unpfxMods = ""
	for mp in zCtx.cpl.modPfxes:
		unpfxMods += "\n - " + unpfxMod(mp)
	zCtx.dbg0("Available modules are :" + unpfxMods)

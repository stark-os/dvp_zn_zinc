#!/usr/bin/python3



# -------- IMPORTATIONS --------

#sys
import os, sys

#std
from std.path import *

#internal
from zctx import *
from pcpl.p1_commentsAndText import *
from pcpl.p2_directives      import *
from pcpl.p3_ZCSAndImp       import *






# -------- TOOLS --------

#prepare a raw parsed ZCI into just the minimum required (useless blanks + expand imports if needed)
#result can be several ZCIs so we directly add them to the result list given as parameter
def stripAndAppendZCI(ZCI, result, allowImpExpansion=False, modPfx=None):
	if modPfx is None:
		modPfx = ""
	ZCI.modPfx = modPfx

	#strip sides
	ZCI.strip()
	ZCIDeepDbg(ZCI, "Stripped blanks from ZCI \"" + ZCI.txtFormat() + '\"', prtSubCtxs=False, prtLine=False)



	# PROCESSING REGULAR/IMPORT ZCI

	#empty ZCI => ignore it
	if len(ZCI.txt) == 0:
		return

	#not long enough to be an import => regular ZCI
	if len(ZCI.txt) < 4:
		ZCIDeepDbg(ZCI, "Detected as non-importation ZCI => Adding it " + ZCI.toStr())
		result.append(ZCI)
		return

	#import ZCI : process it NOW
	if ZCI.txt.startswith("imp") and ZCI.txt[3] in BLANKS:
		ZCIDeepDbg(ZCI, "Detected as importation ZCI => processing it now.")

		#importations not allowed
		if not allowImpExpansion or len(modPfx) != 0:
			ZCIErr(ZCI, "Invalid ZCS: Import ZCIs are only allowed in global scope outside any module.")

		#jump required blank zone
		ZCI.forward(3)                                          #We can foward & jump here because we will not store that ZCI, it will only be used for expanding its importation.
		jumpBlankZone(ZCI, "File path in import ZCI (EXT_IMP)") # Else, we would rather keep our ZCI with a correct ctx starting at its beginning.

		#importation path
		path = readName(ZCI, "File path in import ZCI (EXT_IMP).", blacklist=BLANKS_EXTENDED)[1] #same note as before
		if not ZCI.reachedEnd():
			ZCIErr(ZCI, "Too much elements in import ZCI (EXT_IMP); should stop here.")

		#process import : Will add every ZCI of the imported file instead of the cur one
		if zCtx__openNewSubCtx(ZCI.zCtx, path):

			#precompile imported file
			p1_commentsAndText(ZCI.zCtx)     #these 4 calls should be replaced by a precompile(zCtx) call but python doesn't manage parent-file importation well so...
			p2_directives(ZCI.zCtx)          #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO CHANGE
			result += p3_ZCSAndImp(ZCI.zCtx)
		return

	#not an import => regular ZCI
	ZCIDeepDbg(ZCI, "Detected as non-importation ZCI => Adding it " + ZCI.toStr())
	result.append(ZCI)






# -------- EXECUTION --------

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Pythonic
INT_MAX = sys.maxsize

#split raw text into ZCI list (ZCS)
def extractZCIsFromCtx(zCtx, ctx, gbl=False, subCtxs=None, modPfx=None, wallIdx=INT_MAX): #wallIdx is the ending chr for ZCI extraction: it is not to be included in ZCI, but if reached, we must end right AFTER it.
	zCtx.deepDbg("Extracting ZCIs inside given context.", prtSubCtxs=True)
	if subCtxs is None:
		subCtxs = zCtx.subCtxs

	#initial state
	ZCI          = None
	skipLineFeed = False
	peerIdx      = 0
	reachedWall  = 0

	#parsing byte per byte
	ZCIs = []
	while not ctx.inc():
		c = ctx.get()

		#given limit reached => also stop but cur ZCI must have current chr added too
		if ctx.icontent.idx >= wallIdx:
			reachedWall = 1
			break

		#initialize next ZCI to that position in ctx
		if ZCI is None:
			skipLineFeed = False
			ZCI = newZCI(zCtx, lst_ctx__copy(subCtxs, copyContent=True))



		#1: multi-line ZCI
		if skipLineFeed:
			if c == '\n': #really skipping line feed
				skipLineFeed = False
				continue
			else: #not actually skipping it, that was just a regular backslash
				ZCI.txt += '\\'
				#note that we don't reset skipLineFeed here, we will use it as flag in multi-line ZCI detection to say :
				# "hey! We already had a backslash before so you can ignore the next backslash" (escape sequence)



		#2: end of ZCI
		if c == ';' or c == '\n':
			if len(ZCI.txt) != 0: #tiny optimization
				ZCI.stopIdx = ctx.icontent.idx - 1
				stripAndAppendZCI(ZCI, ZCIs, allowImpExpansion=gbl, modPfx=modPfx)

			#next ZCI
			ZCI = None
			continue



		#3: maybe having a multi-line ZCI
		if c == '\\' and not skipLineFeed:
			skipLineFeed = True
			continue
		skipLineFeed = False



		#4: openning includer found
		if c in INCLUDERS.keys():
			if ctx.icontent.idx in ZCI.pairs.keys(): #already in pairs
				zCtx.int("Processing the same ZCI includer twice.")

			#get every pairs until end of our includer
			curPairs = ctx.getPairsUntilCorrespondingPeer(allowedPairs=INCLUDERS)
			if curPairs == PARSING_CTX__INCONSISTENT_INCLUDER_PARSING:
				zCtx.err("Invalid ZCS: Inconsistent use of includers inside block (opening/closing).")
			if curPairs == PARSING_CTX__PEER_NOT_FOUND:
				zCtx.err("Invalid ZCS: Missing closing includer '" + INCLUDERS[c] + "'.")

			#add these pairs to our ZCI so we can find them more easily if further compilation steps
			for p in curPairs.keys():
				ZCI.pairs[p] = curPairs[p]

			#includers boudaries
			opening = ctx.icontent.idx
			closing = curPairs[opening]

			#store raw includer text into ZCI
			ZCI.txt += str_sub(ctx.icontent.s, opening, closing)

			#step until end of includer
			if ctx.forward(closing - opening):
				zCtx.int("Could not forward to the end of includer (openning at " + str(opening) + ", closing at " + str(closing) + ").")
			continue



		#5: ending includer found (alone)
		if c in INCLUDERS.values():
			zCtx.err("Lonely ending includer found, missing its opening one before.")



		#6: any other regular character
		ZCI.txt += c

	#also add last ZCI remaining
	if ZCI is not None:
		ZCI.stopIdx = ctx.icontent.idx - reachedWall #reached wall => decrease to be right before wallIdx (we don't want the wall to be included in the last ZCI)
		stripAndAppendZCI(ZCI, ZCIs, allowImpExpansion=gbl, modPfx=modPfx)

	#we want to be right AFTER the wall (do nothing if no wall has been reached)
	ctx.forward(reachedWall)

	#return result
	return ZCIs



#main
def p3_ZCSAndImp(zCtx):
	zCtx.step = STEP.P3
	zCtx.dbgSepLine()
	zCtx.dbg("============================================================================")
	zCtx.dbg("======================= P3 ZCS AND IMPs : beginning ========================")
	zCtx.dbg("============================================================================")
	zCtx.dbg("FILE: " + zCtx.ctx.filepath)
	zCtx.deepDbgPause()

	#extract global scope ZCIs
	ZCIs = extractZCIsFromCtx(zCtx, zCtx.ctx, gbl=True)

	#debug
	zCtx.dbg("============================================================================")
	zCtx.dbg("========================== P3 ZCS AND IMPs : end ===========================")
	zCtx.dbg("============================================================================")
	zCtx.dbg("FILE: " + zCtx.ctx.filepath)
	zCtx.dbgSepLine()
	zCtx.deepDbgPause()

	#debug
	if zCtx.dbgMode[zCtx.step]:
		prepareDbgDir()
		dumpZCIs(ZCIs, "dbg/" + path_name(zCtx.ctx.filename) + ".p3.dl")

	#no need cur context anymore (end of precompilation by the way)
	zCtx__closeCurrentCtx(zCtx)

	#return list of precompiled ZCIs
	return ZCIs

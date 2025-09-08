#!/usr/bin/python3



# -------- IMPORTATIONS --------

#sys
import sys

#std
from std.path import *

#internal
from zctx                       import *
from pcpl.p1_CommentsPItemsText import *
from pcpl.p2_applyConfiguration import *
from pcpl.p3_splitZCIsAndImport import *






# -------- TOOLS --------

#prepare a raw parsed ZCI into just the minimum required (useless blanks + expand imports if needed)
#result can be several ZCIs so we directly add them to the result list given as parameter
def stripAndAppendZCI(zCtx, ZCI, result, allowImportsExpansion=False, modulePrefix=None):
	if modulePrefix is None:
		modulePrefix = ""
	ZCI.modulePrefix = modulePrefix

	#strip sides
	ZCI.strip()
	zCtx.ZCIDeepDebug(ZCI, "Stripped blanks from ZCI " + ZCI.textFormat(), printSubCtxs=False, printLine=False)



	# PROCESSING REGULAR/IMPORT ZCI

	#empty ZCI => ignore it
	if len(ZCI.txt) == 0:
		return

	#not long enough to be an import => regular ZCI
	if len(ZCI.txt) < 4:
		zCtx.ZCIDeepDebug(ZCI, "Detected as non-importation ZCI => Adding it " + ZCI.toStr())
		result.append(ZCI)
		return

	#import ZCI : process it NOW
	if ZCI.txt.startswith("imp") and ZCI.txt[3] in BLANKS:
		zCtx.deepDebug("Detected as importation ZCI => processing it now.")

		#importations not allowed
		if not allowImportsExpansion or len(modulePrefix) != 0:
			zCtx.error("Invalid ZCS: Import ZCIs are only allowed in global scope outside any module.")

		#jump required blank zone
		ZCI.forward(3)                                               #We can foward & jump here because we will not store that ZCI, it will only be used for expanding its importation.
		zCtx.jumpBlankZone(ZCI, "File path in import ZCI (EXT_IMP)") # Else, we would rather keep our ZCI with a correct ctx starting at its beginning.

		#importation path
		path = zCtx.readName(ZCI, "File path in import ZCI (EXT_IMP).", blacklist=BLANKS_EXTENDED) #same note as before
		if not ZCI.reachedEnd():
			zCtx.ZCIError(ZCI, "Too much elements in import ZCI (EXT_IMP); should stop here.")

		#process import : Will add every ZCI of the imported file instead of the current one
		if zCtx.openNewSubCtx(path):

			#precompile imported file
			p1_CommentsPItemsText(zCtx) #these 3 calls should be replaced by a precompile(zCtx) call but python doesn't manage parent-file importation well so...
			p2_applyConfiguration(zCtx) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO CHANGE
			result += p3_splitZCIsAndImport(zCtx)
		return

	#not an import => regular ZCI
	zCtx.ZCIDeepDebug(ZCI, "Detected as non-importation ZCI => Adding it " + ZCI.toStr())
	result.append(ZCI)






# -------- EXECUTION --------

#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< Pythonic
INT_MAX = sys.maxsize

#split raw text into ZCI list (ZCS)
def extractZCIsFromCtx(zCtx, ctx, global_=False, subCtxs=None, modulePrefix=None, maximumIdxAllowed=INT_MAX):
	zCtx.deepDebug("Extracting ZCIs inside given context.", printSubCtxs=True)
	if subCtxs is None:
		subCtxs = zCtx.subCtxs

	#initial state
	ZCI          = None
	skipLineFeed = False
	peerIdx    = 0

	#parsing byte per byte
	ZCIs = []
	while not ctx.inc():
		if ctx.icontent.idx > maximumIdxAllowed:
			break
		c = ctx.get()

		#initialize next ZCI to that position in ctx
		if ZCI is None:
			skipLineFeed = False
			ZCI = newZCI(lst_ctx__copy(subCtxs, copyContent=True))



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
				zCtx.ZCIDeepDebug(ZCI, "Extracted raw ZCI text " + ZCI.textFormat())
				stripAndAppendZCI(zCtx, ZCI, ZCIs, allowImportsExpansion=global_, modulePrefix=modulePrefix)

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
				zCtx.internal("Processing the same ZCI includer twice.")

			#get every pairs until end of our includer
			currentPairs = ctx.getPairsUntilCorrespondingPeer(allowedPairs=INCLUDERS)
			if currentPairs == PARSING_CTX__INCONSISTENT_INCLUDER_PARSING:
				zCtx.error("Invalid ZCS: Inconsistent use of includers inside block (opening/closing).")
			if currentPairs == PARSING_CTX__PEER_NOT_FOUND:
				zCtx.error("Invalid ZCS: Missing closing includer '" + INCLUDERS[c] + "'.")

			#add these pairs to our ZCI so we can find them more easily if further compilation steps
			for p in currentPairs.keys():
				ZCI.pairs[p] = currentPairs[p]

			#includers boudaries
			opening = ctx.icontent.idx
			closing = currentPairs[opening]

			#store raw includer text into ZCI
			ZCI.txt += str_sub(ctx.icontent.s, opening, closing)

			#step until end of includer
			if ctx.forward(closing - opening):
				zCtx.internal("Could not forward to the end of includer (openning at " + str(opening) + ", closing at " + str(closing) + ").")
			continue



		#5: ending includer found (alone)
		if c in INCLUDERS.values():
			zCtx.error("Lonely ending includer found, missing its opening one before.")



		#6: any other regular character
		ZCI.txt += c

	#also add last ZCI remaining
	if ZCI is not None:
		ZCI.stopIdx = ctx.icontent.idx
		stripAndAppendZCI(zCtx, ZCI, ZCIs, allowImportsExpansion=global_, modulePrefix=modulePrefix)

	#return result
	return ZCIs



#main
def p3_splitZCIsAndImport(zCtx):
	zCtx.deepDebug("\n\n\n\n")
	zCtx.deepDebug("============================================================================")
	zCtx.deepDebug("=================== P3 SPLIT ZCIs AND IMPORT : beginning ===================")
	zCtx.deepDebug("============================================================================")
	zCtx.deepDebug("FILE: " + zCtx.ctx.filepath + "\n\n\n\n")
	zCtx.deepDebugPause()

	#extract global scope ZCIs
	ZCIs = extractZCIsFromCtx(zCtx, zCtx.ctx, global_=True)

	#debug
	zCtx.deepDebug("\n\n\n\n")
	zCtx.deepDebug("======================================================================")
	zCtx.deepDebug("=================== P3 SPLIT ZCIs AND IMPORT : end ===================")
	zCtx.deepDebug("======================================================================")
	zCtx.deepDebug("FILE: " + zCtx.ctx.filepath + "\n\n\n\n")
	zCtx.deepDebugPause()

	#debug
	if zCtx.debugMode:
		dumpZCIs(ZCIs, "debug/" + path_name(zCtx.ctx.filename) + ".p3.json")

	#no need current context anymore (end of precompilation by the way)
	zCtx.closeCurrentCtx()

	#return list of precompiled ZCIs
	return ZCIs

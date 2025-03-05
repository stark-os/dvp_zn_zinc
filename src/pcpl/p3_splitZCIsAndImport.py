#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.path import *

#parsing
import std.dreamlands as dl

#internal
from zctx                       import *
from pcpl.p1_CommentsPItemsText import *
from pcpl.p2_applyConfiguration import *
from pcpl.p3_splitZCIsAndImport import *






# -------- TOOLS --------

#prepare a raw parsed ZCI into just the minimum required (useless blanks + expand imports if needed)
#result can be several ZCIs so we directly add them to the result list given as parameter
def stripAndAppendZCI(zCtx, ZCI, result, allowImportsExpansion=False):

	#get REAL beginning of ZCI (prepare for stripping BEGINNING blanks)
	beginningIndex = 0
	lineFeedFound  = False
	for c in ZCI.ctx.icontent.s:

		#as long as we have blanks, shift real beginning of ZCI
		if c in BLANKS:
			beginningIndex += 1
			if lineFeedFound: #if at least 1 line feed has been found, we MUST count columnNbr
				ZCI.ctx.columnNbr += 1

		#line feed found => ZCI does not start at current lineNbr, it may be next line (or further)
		elif c == '\n':
			lineFeedFound     = True
			beginningIndex   += 1
			ZCI.ctx.lineNbr  += 1 #lineNbr/columnNbr were not totally accurate
			ZCI.ctx.columnNbr = 1 # => we must count them again starting from where we were

		#any other character => beginning of ZCI => stop stripping here
		else:
			break

	#strip BEGINNING blanks
	ZCI.ctx.icontent.s = ZCI.ctx.icontent.s[beginningIndex:]

	#strip END blanks
	ZCI.ctx.icontent.s = str_stripEnd(ZCI.ctx.icontent.s, BLANKS)
	ZCIText = ZCI.ctx.icontent.s

	#reset ZCI ctx parsing (not lineNbr/columnNbr) for blank/name parsing
	ZCI.ctx.icontent.index = -1
	ZCI.ctx.detectedLF     = False

	#empty ZCI => ignore it
	if len(ZCIText) == 0:
		return

	#not long enough to be an import => regular ZCI
	if len(ZCIText) < 5:
		result.append(ZCI)

	#import ZCI : process it NOW
	if ZCIText.startswith("imp") and ZCIText[3] in BLANKS:
		ZCI.ctx.forward(4)

		#importations not allowed
		if not allowImportsExpansion:
			zCtx.error("Invalid ZCS: Import ZCIs are only allowed in global scope.")

		#read path
		zCtx.jumpBlankZone(ZCI.ctx, "File path in import ZCI (EXT_IMP)")

		#no path given
		path = zCtx.readName(ZCI.ctx, "File path in import ZCI (EXT_IMP).")

		#process import : Will add every ZCI of the imported file instead of the current one
		if zCtx.openNewSubCtx(path):

			#precompile imported file
			p1_CommentsPItemsText(zCtx) #these 3 calls should be replaced by a precompile(zCtx) call but python doesn't manage parent-file importation well so...
			p2_applyConfiguration(zCtx) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO CHANGE
			result += p3_splitZCIsAndImport(zCtx)
		return

	#not an import => regular ZCI
	result.append(ZCI)






# -------- EXECUTION --------

#split raw text into ZCI list (ZCS)
def extractZCIsFromCtx(zCtx, ctx, global_=False):

	#initial state
	ZCIUninitialized = True
	skipLineFeed     = False
	peerIndex        = 0

	#prepare current ZCI result : Keep the same lineNbr/columnNbr/filename/... BUT changing the icontent inside.
	ZCI = zci(ctx.copy())       # It will start as it was a totally new content but we keep the old file position for error indication.
	ZCI.ctx.icontent.index = -1
	ZCI.ctx.icontent.s     = "" # length=0 (can be weird cause we may have big lineNbr/columnNbr)

	#prepare whole result
	ZCIs = []

	#parsing byte per byte
	while not ctx.inc():
		c = ctx.get()



		#1) in includer
		if peerIndex != 0:

			#end of our includer => return to regular parsing
			if peerIndex == ctx.icontent.index:
				peerIndex = 0



		#2) outside any includer
		else:

			#multi-line ZCI
			if skipLineFeed:
				if c == '\n': #really skipping line feed
					skipLineFeed       = False
					ZCI.ctx.icontent.s += '\n' #storing the line feed in all cases => necessary to get consistent BEGINNING lineNbr/columnNbr of ZCI when stripping it
					continue
				else: #not actually skipping it, that was just a regular backslash
					ZCI.ctx.icontent.s += '\\'

			#end of ZCI
			if c == ';' or c == '\n':
				stripAndAppendZCI(zCtx, ZCI, ZCIs, allowImportsExpansion=global_)
				ZCI                = zci(ctx.copy()) #reset current ZCI result
				ZCI.ctx.icontent.s = ""              # length=0 : really important to reset length
				ZCIUninitialized  = True
				continue

			#maybe having a multi-line ZCI
			if c == '\\':
				skipLineFeed = True
				continue

			#includer found
			if c in INCLUDERS.keys():
				peerIndex = ctx.getCorrespondingPeerIndex(peers=INCLUDERS)
				if peerIndex == -2:
					zCtx.error("Invalid ZCS: Inconsistent use of includers inside block (opening/closing).")
				if peerIndex == -3:
					zCtx.error("Invalid ZCS: Missing closing includer '" + INCLUDERS[c] + "'.")



		#3) regular case
		if ZCIUninitialized: #init current ZCI with its real position in file
			ZCIUninitialized  = False
			ZCI.ctx.lineNbr   = ctx.lineNbr
			ZCI.ctx.columnNbr = ctx.columnNbr
		ZCI.ctx.icontent.s += c

	#last ZCI remaining
	stripAndAppendZCI(zCtx, ZCI, ZCIs, allowImportsExpansion=global_)

	#return result
	return ZCIs



#main
def p3_splitZCIsAndImport(zCtx):

	#extract global scope ZCIs
	ZCIs = extractZCIsFromCtx(zCtx, zCtx.ctx, True)

	#debug
	if zCtx.debugMode:
		debugOutput = ""
		for ZCI in ZCIs:
			debugOutput += ZCI.ctx.toStr() + "\"" + ZCI.ctx.icontent.s + "\"\n"
		writeFile("debug/" + path_name(zCtx.ctx.filename) + ".p3.lst", debugOutput)

	#no need current context anymore (end of precompilation by the way)
	zCtx.closeCurrentCtx()

	#return list of precompiled ZCIs
	return ZCIs

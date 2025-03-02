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

#prepare a raw parsed ZCI text zone into just the minimum required (useless blanks + expand imports if needed)
#result can be several ZCIs so we directly add them to the result list given as parameter
def stripAndAppendZCI(zCtx, ZCICtx, result, allowImportsExpansion=False):

	#get REAL beginning of ZCI (prepare for stripping BEGINNING blanks)
	beginningIndex = 0
	lineFeedFound  = False
	for c in ZCICtx.icontent.s:

		#as long as we have blanks, shift real beginning of ZCI
		if c in BLANKS:
			beginningIndex += 1
			if lineFeedFound: #if at least 1 line feed has been found, we MUST count columnNbr
				zci_columnNbr += 1

		#line feed found => ZCI does not start at current lineNbr, it may be next line (or further)
		elif c == '\n':
			lineFeedFound     = True
			beginningIndex   += 1
			ZCICtx.lineNbr   += 1 #lineNbr/columnNbr were not totally accurate
			ZCICtx.columnNbr  = 1 # => we must count them again starting from where we were

		#any other character => beginning of ZCI => stop stripping here
		else:
			break

	#strip BEGINNING blanks
	ZCICtx.icontent.s = ZCICtx.icontent.s[beginningIndex:]

	#strip END blanks
	ZCICtx.icontent.s = str_stripEnd(ZCICtx.icontent.s, BLANKS)

	#empty ZCI => ignore it
	if len(ZCICtx.icontent.s) == 0:
		return

	#not long enough to be an import => regular ZCI
	if len(ZCICtx.icontent.s) < 5:
		result.append(ZCICtx)

	#import ZCI : process it NOW
	s = ZCICtx.icontent.s
	if s.startswith("imp") and s[3] in BLANKS:
		if not allowImportsExpansion:
			zCtx.error("Invalid ZCS: Import ZCIs are only allowed in global scope.")

		#strip beginning of path
		pathNotFound       = True
		pathBeginningIndex = 4
		while pathBeginningIndex < len(s):
			if s[pathBeginningIndex] in BLANKS:
				pathBeginningIndex += 1
				continue
			else:
				pathNotFound = False
				break

		#no path given
		if pathNotFound:
			zCtx.error("Missing path for import ZCI (EXT_IMP).")

		#process import : Will add every ZCI of the imported file instead of the current one
		if zCtx.openNewSubCtx(s[pathBeginningIndex:]):

			#precompile imported file
			p1_CommentsPItemsText(zCtx) #these 3 calls should be replaced by a precompile(zCtx) call but python doesn't manage parent-file importation well so...
			p2_applyConfiguration(zCtx) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< TO CHANGE
			result += p3_splitZCIsAndImport(zCtx)
		return

	#not an import => regular ZCI
	result.append(ZCICtx)






# -------- EXECUTION --------

#split raw text into ZCI list (ZCS)
def extractZCIsFromCtx(zCtx, ctx, global_=False):

	#initial state
	ZCIUninitialized = True
	skipLineFeed     = False
	peerIndex        = 0

	#prepare current ZCI result : Keep the same lineNbr/columnNbr/filename/... BUT changing the icontent inside.
	ZCICtx = ctx.copy()         # It will start as it was a totally new content but we keep the old file position for error indication.
	ZCICtx.icontent.index = -1
	ZCICtx.icontent.s     = ""  # length=0 (can be weird cause we may have big lineNbr/columnNbr)

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
					ZCICtx.icontent.s += '\n' #storing the line feed in all cases => necessary to get consistent BEGINNING lineNbr/columnNbr of ZCI when stripping it
					continue
				else: #not actually skipping it, that was just a regular backslash
					ZCICtx.icontent.s += '\\'

			#end of ZCI
			if c == ';' or c == '\n':
				stripAndAppendZCI(zCtx, ZCICtx, ZCIs, allowImportsExpansion=global_)
				ZCICtx            = ctx.copy() #reset current ZCI result
				ZCICtx.icontent.s = ""         # length=0 : really important to reset length
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
			ZCIUninitialized = False
			ZCICtx.lineNbr   = ctx.lineNbr
			ZCICtx.columnNbr = ctx.columnNbr
		ZCICtx.icontent.s += c

	#last ZCI remaining
	stripAndAppendZCI(zCtx, ZCICtx, ZCIs, allowImportsExpansion=global_)

	#return result
	return ZCIs



#main
def p3_splitZCIsAndImport(zCtx):

	#extract global scope ZCIs
	ZCIs = extractZCIsFromCtx(zCtx, zCtx.ctx, True)

	#debug
	if zCtx.debugMode:
		debugOutput = ""
		for z in ZCIs:
			debugOutput += z.toStr() + "\"" + z.icontent.s + "\"\n"
		writeFile("debug/" + path_name(zCtx.ctx.filename) + ".p3.lst", debugOutput)

	#no need current context anymore (end of precompilation by the way)
	zCtx.closeCurrentCtx()

	#return list of precompiled ZCIs
	return ZCIs

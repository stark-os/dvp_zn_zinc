#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.path import *

#parsing
import std.dreamlands as dl

#internal
from zctx import *
from pcpl.p1_CommentsPItemsText import *
from pcpl.p2_applyConfiguration import *
from pcpl.p3_splitZCIsAndImport import *






# -------- TOOLS --------

#add a ZCI that has been parsed in global scope (local scope ZCIs are not parsed for the moment)
def appendZCIExpandingImports(zCtx, zci_lineNbr, zci_columnNbr, ZCIText):

	#get REAL beginning of ZCI (prepare for stripping BEGINNING blanks)
	beginningIndex = 0
	lineFeedFound  = False
	for c in ZCIText:

		#as long as we have blanks, shift real beginning of ZCI
		if c in BLANKS:
			beginningIndex += 1
			if lineFeedFound: #if at least 1 line feed has been found, we MUST count columnNbr
				zci_columnNbr += 1

		#line feed found => ZCI really starts in next line
		elif c == '\n':
			lineFeedFound   = True
			beginningIndex += 1
			zci_lineNbr    += 1 #line/columnNbr were not accurate
			zci_columnNbr   = 1 # => we must count them again starting from were we were
		else:
			break

	#strip BEGINNING blanks
	ZCIText = ZCIText[beginningIndex:]

	#line feeds are no longer useful in our ZCI => getting rid of them
	ZCIText = ZCIText.replace("\n", "") #.removeAllChr('\n')

	#strip END blanks
	ZCIText = ZCIText.strip() #.stripEnd(BLANKS)

	#empty ZCI => ignore it
	if len(ZCIText) == 0:
		return

	#not long enough to be an import => regular ZCI
	if len(ZCIText) < 5:
		zCtx.appendZCI(ZCIText, zci_lineNbr, zci_columnNbr)
		return

	#import ZCI : process it NOW
	if ZCIText.startswith("imp") and ZCIText[3] in BLANKS:
		pathNotFound       = True
		pathBeginningIndex = 4
		while pathBeginningIndex < len(ZCIText):
			if ZCIText[pathBeginningIndex] in BLANKS:
				pathBeginningIndex += 1
				continue
			else:
				pathNotFound = False
				break

		#no path given
		if pathNotFound:
			zCtx.error("Missing path for import ZCI (EXT_IMP).")

		#process import
		prevCtxText = zCtx.ctx.toStr()
		if zCtx.openNewSubCtx(ZCIText[pathBeginningIndex:]):
			p1_CommentsPItemsText(zCtx)
			p2_applyConfiguration(zCtx)
			p3_splitZCIsAndImport(zCtx)
		return

	#not an import => regular ZCI
	zCtx.appendZCI(ZCIText, zci_lineNbr, zci_columnNbr)






# -------- EXECUTION --------

#split raw text into ZCI list (ZCS)
def p3_splitZCIsAndImport(zCtx):
	skipLineFeed = False
	ZCIText      = ""
	peerIndex    = 0

	#ZCI beginning indication (works in pair : here, -1 to column means "undefined yet")
	zci_columnNbr = -1
	zci_lineNbr   =  1

	#includer start indication (for errors only)
	i_colmNbr    = 0
	i_lineNbr    = 0

	#parsing byte per byte
	while not zCtx.inc():
		c = zCtx.get()



		#1) in includer
		if peerIndex != 0:

			#end of our includer => return to regular parsing
			if peerIndex == zCtx.ctx.icontent.index:
				peerIndex = 0



		#2) outside any includer
		else:

			#multi-line ZCI
			if skipLineFeed:
				if c == '\n': #really skipping line feed
					skipLineFeed  = False
					ZCIText      += '\n' #storing the line feed in all cases => necessary to get consistent BEGINNING ctx of ZCI when stripping it
					continue
				else: #not actually skipping it, that was just a regular backslash
					ZCIText += '\\'

			#end of ZCI
			if c == ';' or c == '\n':
				appendZCIExpandingImports(zCtx, zci_lineNbr, zci_columnNbr, ZCIText)
				zci_columnNbr = -1 #reset current ZCI
				ZCIText       = ""
				continue

			#maybe a multi-line ZCI
			if c == '\\':
				skipLineFeed = True
				continue

			#includer found
			if c in INCLUDERS.keys():
				i_lineNbr = zCtx.ctx.lineNbr   #for error indication only
				i_colmNbr = zCtx.ctx.columnNbr
				peerIndex = zCtx.ctx.getCorrespondingPeerIndex(peers=INCLUDERS)
				if peerIndex == -2:
					zCtx.error("Invalid ZCS: Inconsistent use of includers inside block (opening/closing).")
				if peerIndex == -3:
					zCtx.error("Invalid ZCS: Missing closing includer '" + INCLUDERS[c] + "'.")



		#3) regular case
		if zci_columnNbr == -1: #objective: get ctx of the BEGINNING of our current ZCI
			zci_lineNbr   = zCtx.ctx.lineNbr
			zci_columnNbr = zCtx.ctx.columnNbr
		ZCIText += c

	#still in includer
	if peerIndex != 0:
		zCtx.error("Invalid ZCS: End of file reached before closing includer at location " + str(i_lineNbr) + ":" + str(i_colmNbr))

	#last ZCI remaining
	appendZCIExpandingImports(zCtx, zci_lineNbr, zci_columnNbr, ZCIText)

	#debug
	if zCtx.debugMode:
		debugOutput = ""
		for p in zCtx.pcpl.ZCIs:
			debugOutput += p.ctx.toStr() + "\"" + p.text + "\"\n"
		writeFile("debug/" + path_name(zCtx.ctx.filename) + ".p3.lst", debugOutput)

	#no need current context anymore (end of precompilation by the way)
	zCtx.closeCurrentCtx()

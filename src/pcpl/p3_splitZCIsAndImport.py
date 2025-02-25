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
def appendZCIExpandingImports(zCtx, ZCIText):
	ZCIBeginningColumnNbr = zCtx.ctx.columnNbr - len(ZCIText)

	#measure beginning blank offset
	beginningIndex = 0
	for c in ZCIText:
		if c in BLANKS:
			beginningIndex += 1
		else:
			break
	ZCIBeginningColumnNbr += beginningIndex #adjust ZCI columnNbr

	#strip blanks
	ZCIText = ZCIText[beginningIndex:]
	ZCIText = ZCIText.strip()          #stripEnd() would be more appropriate here

	#empty ZCI => ignore it
	if len(ZCIText) == 0:
		return

	#not long enough to be an import => regular ZCI
	if len(ZCIText) < 5:
		zCtx.appendZCI(ZCIText, ZCIBeginningColumnNbr)
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
		zCtx.openNewSubCtx(ZCIText[pathBeginningIndex:])
		p1_CommentsPItemsText(zCtx)
		p2_applyConfiguration(zCtx)
		p3_splitZCIsAndImport(zCtx)
		return

	#not an import => regular ZCI
	zCtx.appendZCI(ZCIText, ZCIBeginningColumnNbr)






# -------- EXECUTION --------

#split raw text into ZCI list (ZCS)
def p3_splitZCIsAndImport(zCtx):
	skipLineFeed = False
	ZCIText      = ""
	peerIndex    = 0
	i_colmNbr    = 0 #for error indication only
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
					skipLineFeed = False
					continue
				else: #not actually skipping it, that was just a regular backslash
					ZCIText += '\\'

			#end of ZCI
			if c == ';' or c == '\n':
				appendZCIExpandingImports(zCtx, ZCIText)
				ZCIText = ""
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
					zCtx.error("Invalid ZCS: Missing closing includer '" + includers[c] + "' in current file.")



		#3) regular case
		ZCIText += c

	#still in includer
	if peerIndex != 0:
		zCtx.error("Invalid ZCS: End of file reached before closing includer at location " + str(i_lineNbr) + ":" + str(i_colmNbr))

	#last ZCI remaining
	appendZCIExpandingImports(zCtx, ZCIText)

	#debug
	if zCtx.debugMode:
		debugOutput = ""
		for p in zCtx.pcpl.ZCIs:
			debugOutput += p.ctx.filepath + ":" + str(p.ctx.lineNbr) + ":" + str(p.ctx.columnNbr) + "] \"" + p.text + "\"\n"
		writeFile(path_name(zCtx.ctx.filename) + ".p3.lst", debugOutput)

	#no need current context anymore (end of precompilation by the way)
	zCtx.closeCurrentCtx()

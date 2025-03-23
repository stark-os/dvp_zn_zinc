#!/usr/bin/python3



# -------- IMPORTATIONS --------

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
def stripAndAppendZCI(zCtx, ZCI, result, allowImportsExpansion=False, modulePrefix=""):
	ZCI.modulePrefix = modulePrefix



	# 1) STRIPPING SIDES

	#strip BEGINNING blanks
	beginningShift = str_getBeginningStripIndex(ZCI.ctx.icontent.s, charset=BLANKS_EXTENDED)
	for a in range(beginningShift): #we must strip in 2-step to keep a consistent ctx (lineNbr & colmNbr)
		ZCI.inc()
	ZCI.ctx.icontent.s = str_sub(ZCI.ctx.icontent.s, start=beginningShift)

	#shift ZCI pairs indexes with the new beginning
	newPairs = {}
	for p in ZCI.pairs.keys():
		newPairs[p-beginningShift] = ZCI.pairs[p] - beginningShift
	ZCI.pairs = newPairs

	#strip END blanks
	ZCI.ctx.icontent.s = str_stripEnd(ZCI.ctx.icontent.s, BLANKS_EXTENDED)
	ZCIText            = ZCI.ctx.icontent.s



	# 2) PROCESSING REGULAR/IMPORT ZCI

	#reset ZCI ctx parsing (not lineNbr/colmNbr) for blank/name parsing
	ZCI.ctx.icontent.index = -1
	ZCI.ctx.detectedLF     = False

	#empty ZCI => ignore it
	if len(ZCIText) == 0:
		return

	#not long enough to be an import => regular ZCI
	if len(ZCIText) < 4:
		result.append(ZCI)
		return

	#import ZCI : process it NOW
	if ZCIText.startswith("imp") and ZCIText[3] in BLANKS:

		#importations not allowed
		if not allowImportsExpansion or len(modulePrefix) != 0:
			zCtx.error("Invalid ZCS: Import ZCIs are only allowed in global scope outside any module.")

		#jump required blank zone
		ZCI.forward(3)
		zCtx.jumpBlankZone(ZCI, "File path in import ZCI (EXT_IMP)")

		#importation path
		path = zCtx.readName(ZCI, "File path in import ZCI (EXT_IMP).", blacklist=BLANKS)
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
	result.append(ZCI)






# -------- EXECUTION --------

#split raw text into ZCI list (ZCS)
def extractZCIsFromCtx(zCtx, ctx, global_=False, subCtxs=None, modulePrefix=""):
	if subCtxs is None:
		subCtxs = zCtx.subCtxs

	#initial state
	ZCIUninitialized = True
	skipLineFeed     = False
	peerIndex        = 0

	#prepare current ZCI result : Keep the same lineNbr/colmNbr/filename/... BUT changing the icontent inside.
	ZCI = zci(ctx.copy(), lst_ctx__copy(subCtxs)) # It will start as it was a totally new content but we keep the old file position for error indication.
	ZCI.ctx.icontent.index = -1
	ZCI.ctx.icontent.s     = "" # length=0 (can be weird cause we may have big lineNbr/colmNbr)

	#overwrite latest subCtx with a reference to the active one (it will change during parsing)
	ZCI.subCtxs[-1] = ZCI.ctx

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
					skipLineFeed        = False
					ZCI.ctx.icontent.s += '\n' #storing the line feed in all cases => necessary to get consistent BEGINNING lineNbr/colmNbr of ZCI when stripping it
					continue
				else: #not actually skipping it, that was just a regular backslash
					ZCI.ctx.icontent.s += '\\'

			#end of ZCI
			if c == ';' or c == '\n':
				stripAndAppendZCI(zCtx, ZCI, ZCIs, allowImportsExpansion=global_, modulePrefix=modulePrefix)
				ZCI                = zci(ctx.copy(), lst_ctx__copy(subCtxs)) #reset current ZCI result
				ZCI.ctx.icontent.s = "" # length=0 : really important to reset length
				ZCI.subCtxs[-1]    = ZCI.ctx #update latest subCtx as well
				ZCIUninitialized   = True
				continue

			#maybe having a multi-line ZCI
			if c == '\\':
				skipLineFeed = True
				continue

			#includer found
			if c in INCLUDERS.keys():
				ZCI_ctx_icontent_s_len = len(ZCI.ctx.icontent.s) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< only in python (.length field)
				if ZCI_ctx_icontent_s_len in ZCI.pairs:
					zCtx.internal("Processing the same ZCI includer twice.")
				peerIndex = ctx.getCorrespondingPeerIndex(peers=INCLUDERS)
				if peerIndex == -2:
					zCtx.error("Invalid ZCS: Inconsistent use of includers inside block (opening/closing).")
				if peerIndex == -3:
					zCtx.error("Invalid ZCS: Missing closing includer '" + INCLUDERS[c] + "'.")

				#add this pair to our ZCI so we can find them more easily if further compilation steps
				ZCI.pairs[ZCI_ctx_icontent_s_len] = ZCI_ctx_icontent_s_len + (peerIndex - ctx.icontent.index)



		#3) regular case
		if ZCIUninitialized: #init current ZCI with its real position in file
			ZCIUninitialized = False
			ZCI.ctx.lineNbr  = ctx.lineNbr
			ZCI.ctx.colmNbr  = ctx.colmNbr
		ZCI.ctx.icontent.s += c

	#last ZCI remaining
	stripAndAppendZCI(zCtx, ZCI, ZCIs, allowImportsExpansion=global_, modulePrefix=modulePrefix)

	#return result
	return ZCIs



#main
def p3_splitZCIsAndImport(zCtx):

	#extract global scope ZCIs
	ZCIs = extractZCIsFromCtx(zCtx, zCtx.ctx, global_=True)

	#debug
	if zCtx.debugMode:
		debugOutput = "[\n"
		for ZCI in ZCIs:
			content      = ZCI.ctx.icontent.s.replace("\\", "\\\\").replace("\t", "\\t").replace("\n", "\\n")
			debugOutput += "{module:\"" + ZCI.modulePrefix + "\",ctx:\"" + ZCI.ctx.toStr() + "\",content:\"" + content + "\",pairs:\"" + str(ZCI.pairs).replace(' ', '') + "\"},\n"
		debugOutput += "]"
		writeFile("debug/" + path_name(zCtx.ctx.filename) + ".p3.json", debugOutput)

	#no need current context anymore (end of precompilation by the way)
	zCtx.closeCurrentCtx()

	#return list of precompiled ZCIs
	return ZCIs

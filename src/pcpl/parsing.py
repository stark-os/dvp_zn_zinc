#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from pcpl.arithmetic import *
from zctx import *






# -------- PARSING TOOLS --------

#spacing
def PCPL__jumpBlankZone(zCtx, directiveName):

	#expecting to still have things to read
	if zCtx__reachedEnd(zCtx):
		zCtx.err("Precompiler directive " + directiveName + " expected to have something else to read after here.")

	#expecting to be on a blank
	c = zCtx__get(zCtx)
	if c not in BLANKS:
		zCtx.err("Precompiler directive " + directiveName + " expected to have a blank zone here.")

	#read until no more blank
	while True:
		if zCtx__inc(zCtx):
			zCtx.err("Precompiler directive " + directiveName + "expected something after blank zone.")

		#check whether we are still in blank zone (only way out without error)
		if zCtx__get(zCtx) not in BLANKS:
			return



#blocks
def PCPL__readIncluderBlock(zCtx, opening='{'): #result will be the INTERNAL content of includer, so openning & closing chr are NOT INCLUDED
	if zCtx__get(zCtx) != opening:
		zCtx.err("Expected an openning '" + opening + "' includer here.")

	#find corresponding peer
	curPairs = zCtx.ctx.getPairsUntilCorrespondingPeer(
		allowedPairs= { opening: INCLUDERS[opening] }
	)

	#error cases, limited though: only 1 includer type taken into account => cannot have inconsistency
	if curPairs == PARSING_CTX__PEER_NOT_FOUND:
		zCtx.err("Missing end delimiter in braces includer block (corresponding '}').")
	peerIdx = curPairs[zCtx.ctx.icontent.idx]

	#read block content
	block = ""
	while not zCtx__inc(zCtx):
		c = zCtx__get(zCtx)

		#end of block
		if zCtx.ctx.icontent.idx == peerIdx:
			zCtx__inc(zCtx) #set itself right after block
			return block

		#read whatever is inside
		block += c

	#should never occur
	zCtx.int("Reached end of PCPL braces includer block without having errors when getting corresponding pairs.")

def PCPL__readUntil(zCtx, stopCharset):
	block = zCtx__get(zCtx)
	while not zCtx__inc(zCtx):
		c = zCtx__get(zCtx)

		#reached something in stop charset => end here
		if c in stopCharset:
			return block

		#add to block
		block += c

	#end of file => return also
	return block



#item related
def PCPL__readItemValue(zCtx):
	c = zCtx__get(zCtx)

	#having a braces includer => not a value
	if c == '{':
		zCtx.err("Expecting to have a precompiler value here, got braces includer.")

	#case 2: consider having literal text
	txt = PCPL__readUntil(zCtx, BLANKS_EXTENDED)

	#sub directive => can't process now
	if '#' in txt:
		return None
	return txt

def PCPL__checkNameCharset(zCtx, name):
	for c in name:
		if c not in PCPL__NAME_CHARSET:
			zCtx.err("Expected a valid precompiler name (invalid character '" + c + "' found).")

def PCPL__getItemText(zCtx, name):

	#in priority, look in those loaded in cfg/pcpl_itms.cfg (prioritary)
	for i in zCtx.pcpl.inCfgItms.keys():
		if i == name:
			return zCtx.pcpl.inCfgItms[i]

	#then look for code internal definitions
	for i in zCtx.pcpl.inCodeItms.keys():
		if i == name:
			return zCtx.pcpl.inCodeItms[i]

	#not found
	return None

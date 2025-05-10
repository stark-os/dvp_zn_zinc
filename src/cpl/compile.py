#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize     import *
from cpl.c02_redirectGlobal import *






# -------- EXECUTION --------

#compilation
def compile(zCtx, DEBUG_MODES, DEEP_DEBUG_MODES):

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< should not be, this enm is in src/main.py (should be accessible as global CONSTANT dataitem)
	P3  = 0
	C01 = 1
	C02 = 2
	C03 = 3

	#step c01
	zCtx.debugMode     = DEBUG_MODES[C01]
	zCtx.deepDebugMode = DEEP_DEBUG_MODES[C01]
	c01_unmodulize(zCtx)

	#step c02
	zCtx.debugMode     = DEBUG_MODES[C02]
	zCtx.deepDebugMode = DEEP_DEBUG_MODES[C02]
	c02_redirectGlobal(zCtx)

	#step c03
	zCtx.debugMode     = DEBUG_MODES[C03]
	zCtx.deepDebugMode = DEEP_DEBUG_MODES[C03]
	#c02_redirectGlobal(zCtx)

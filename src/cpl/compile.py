#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize              import *
from cpl.c02_redirectGlobal          import *
from cpl.c03_processFunctionContents import *






# -------- EXECUTION --------

#compilation
def compile(zCtx, DBG_MODES, DEEP_DBG_MODES):

	#<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< should not be; this enm is in src/main.py (should be accessible as global CONSTANT dataitem)
	DBG__INIT = 0
	DBG__P3   = 1
	DBG__C01  = 2
	DBG__C02  = 3
	DBG__C03  = 4

	#step c01
	zCtx.debugMode     = DBG_MODES[DBG__C01]
	zCtx.deepDebugMode = DEEP_DBG_MODES[DBG__C01]
	c01_unmodulize(zCtx)

	#step c02
	zCtx.debugMode     = DBG_MODES[DBG__C02]
	zCtx.deepDebugMode = DEEP_DBG_MODES[DBG__C02]
	c02_redirectGlobal(zCtx)

	#step c03
	zCtx.debugMode     = DBG_MODES[DBG__C03]
	zCtx.deepDebugMode = DEEP_DBG_MODES[DBG__C03]
	c03_processFunctionContents(zCtx)

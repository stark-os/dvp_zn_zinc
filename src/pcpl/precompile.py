#!/usr/bin/python3



# -------- IMPORTATIONS --------

#precompilation steps
from pcpl.p1_commentsPItemsText import *
from pcpl.p2_applyConfiguration import *
from pcpl.p3_splitZCIsAndImport import *






# -------- EXECUTION --------

#compilation
def precompile(zCtx):

	#step p1
	p1_commentsPItemsText(zCtx)

	#step p2
	p2_applyConfiguration(zCtx)

	#step p3
	#zCtx.debugMode     = DBG_MODES[DBG__P3] #<<<<<<<<<<<<<<<<<<<<< SHOULD WORK IN Z BUT HERE... YOU KNOW, PYTHON...
	#zCtx.deepDebugMode = DEEP_DBG_MODES[DBG__P3]
	return p3_splitZCIsAndImport(zCtx)

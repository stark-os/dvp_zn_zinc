#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize  import *
from cpl.c02_redirectGbl import *
from cpl.c03_processLcls import *
from cpl.c04_unparseAsC  import *






# -------- EXECUTION --------

#compilation
def compile(zCtx):

	#step c01
	c01_unmodulize(zCtx)

	#step c02
	c02_redirectGbl(zCtx)

	#step c03
	c03_processLcls(zCtx)

	#step c04
	c04_unparseAsC(zCtx)

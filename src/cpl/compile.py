#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize          import *
from cpl.c02_redirectGbl         import *
from cpl.c03_processLcls         import *
from cpl.c04_ffaFcts             import *
from cpl.c05_ZZZ                 import *
from cpl.c06_mergeConsecutiveAsg import *
from cpl.c07_dcpSubVals          import *
from cpl.c08_unparseAsC          import *






# -------- EXECUTION --------

#compilation
def compile(zCtx):
	c01_unmodulize(zCtx)
	c02_redirectGbl(zCtx)
	c03_processLcls(zCtx)
	c04_ffaFcts(zCtx)
	c05_ZZZ(zCtx)
	c06_mergeGblAsg(zCtx)
	c07_dcpSubVals(zCtx)
	c08_unparseAsC(zCtx)

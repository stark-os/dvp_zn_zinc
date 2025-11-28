#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize          import *
from cpl.c02_redirectGbl         import *
from cpl.c03_processLcls         import *
from cpl.c04_ffaFcts             import *
from cpl.c05_atm                 import *
from cpl.c06_toStr               import *
from cpl.c07_mergeConsecutiveAsg import *
from cpl.c08_dcpSubCalls         import *
from cpl.c09_unparseAsC          import *






# -------- EXECUTION --------

#compilation
def compile(zCtx):
	c01_unmodulize(zCtx)
	c02_redirectGbl(zCtx)
	c03_processLcls(zCtx)
	c04_ffaFcts(zCtx)
	c05_atm(zCtx)
	c06_toStr(zCtx)
	c07_mergeConsecutiveAsg(zCtx)
	c08_dcpSubCalls(zCtx)
	c09_unparseAsC(zCtx)

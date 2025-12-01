#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize   import *
from cpl.c02_redirectGbl  import *
from cpl.c03_processLcls  import *
from cpl.c04_xxxx         import *
from cpl.c05_xxxx         import *
from cpl.c06_dcpSubVals   import *
from cpl.c07_rmUncalled   import *
from cpl.c08_unparseAsObv import * #from cpl.c08_unparseAsC  import *






# -------- EXECUTION --------

#compilation
def compile(zCtx):
	c01_unmodulize(zCtx)
	c02_redirectGbl(zCtx)
	c03_processLcls(zCtx)
	c04_xxxx(zCtx)
	c05_xxxx(zCtx)
	c06_dcpSubVals(zCtx)
	c07_rmUncalled(zCtx)
	c08_unparseAsObv(zCtx) #c08_unparseAsC(zCtx)

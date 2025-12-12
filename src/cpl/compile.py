#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize    import *
from cpl.c02_redirectGbl   import *
from cpl.c03_processLcls   import *
from cpl.c04_dcpSubVals    import *
from cpl.c05_unusedFcts    import *
from cpl.c06_bigParamAsRef import *
from cpl.c07_unparseAsObv  import *
from cpl.c08_transitiveCpy import *
from cpl.c09_rmUnreadLcls  import *






# -------- EXECUTION --------

#compilation
def compile(zCtx):
	c01_unmodulize(zCtx)
	c02_redirectGbl(zCtx)
	c03_processLcls(zCtx)
	c04_dcpSubVals(zCtx)
	c05_unusedFcts(zCtx)
	c06_bigParamAsRef(zCtx)
	c07_unparseAsObv(zCtx)
	#c08_transitiveCpy(zCtx)
	#c09_rmUnreadLcls(zCtx)

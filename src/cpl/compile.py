#!/usr/bin/python3



# -------- IMPORTATIONS --------

#internal
from cpl.c01_unmodulize    import *
from cpl.c02_redirectGbl   import *
from cpl.c03_processLcls   import *
from cpl.c04_scpHeadrFootr import *
from cpl.c05_dcpSubVals    import *
from cpl.c06_unusedFcts    import *
from cpl.c07_bigParamAsRef import *
from cpl.c08_unparseAsObv  import *
from cpl.c09_transitiveCpy import *
from cpl.c10_rmUnreadLcls  import *






# -------- EXECUTION --------

#compilation
def compile(zCtx):
	c01_unmodulize(zCtx)
	c02_redirectGbl(zCtx)
	c03_processLcls(zCtx)
	c04_scpHeadrFootr(zCtx)
	c05_dcpSubVals(zCtx)
	c06_unusedFcts(zCtx)
	c07_bigParamAsRef(zCtx)
	c08_unparseAsObv(zCtx)
	#c09_transitiveCpy(zCtx)
	#c10_rmUnreadLcls(zCtx)

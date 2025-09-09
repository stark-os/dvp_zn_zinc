#!/usr/bin/python3



# -------- IMPORTATIONS --------

#precompilation steps
from pcpl.p1_commentsPItemsText import *
from pcpl.p2_applyConfiguration import *
from pcpl.p3_splitZCIsAndImport import *






# -------- EXECUTION --------

#compilation
def precompile(zCtx):
	p1_commentsPItemsText(zCtx)
	p2_applyConfiguration(zCtx)
	return p3_splitZCIsAndImport(zCtx)

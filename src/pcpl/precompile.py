#!/usr/bin/python3



# -------- IMPORTATIONS --------

#precompilation steps
from pcpl.p1_CommentsPItemsText import *
from pcpl.p2_applyConfiguration import *
from pcpl.p3_splitZCIsAndImport import *






# -------- EXECUTION --------

#compilation
def precompile(zCtx):
	p1_CommentsPItemsText(zCtx)
	p2_applyConfiguration(zCtx)
	p3_splitZCIsAndImport(zCtx)

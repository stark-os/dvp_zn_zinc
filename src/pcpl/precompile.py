#!/usr/bin/python3



# -------- IMPORTATIONS --------

#precompilation steps
from pcpl.p1_commentsAndText import *
from pcpl.p2_directives      import *
from pcpl.p3_ZCSAndImp       import *






# -------- EXECUTION --------

#compilation
def precompile(zCtx):

	#step p1
	p1_commentsAndText(zCtx)

	#step p2
	p2_directives(zCtx)

	#step p3
	return p3_ZCSAndImp(zCtx)

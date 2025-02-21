#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os, sys
CXD = os.path.dirname(os.path.realpath(sys.argv[0]))
sys.path.append(CXD)

#std
from std.io         import *
from std.path       import *
from std.parsingCtx import *

#config
import std.config as config

#dreamlands
import std.dreamlands as dreamlands

#z parsing
from zctx            import *
from pcpl.precompile import *
from cpl.compile     import *






# -------- DECLARATIONS --------

#debug
DEBUG_MODE = True

#includers
INCLUDER_PARENTHESES = 0
INCLUDER_BRACKETS    = 1
INCLUDER_BRACES      = 2

#scopes
SCOPE_GLOBAL    = 0
SCOPE_FUNCTION  = 1
SCOPE_STATEMENT = 2






# -------- EXECUTION --------

#main
def main():

	#args
	filepath         = sys.argv[1]
	LLI_requirements = config.read(sys.argv[2])

	#prepare output filename
	output_name = path_name(os.path.basename(filepath))
	output_PCPL = output_name + ".pcpl.nc"
	output_CPL  = output_name + ".cpl.nc"

	#z code context
	config.COMMENT_CHARACTER         = '%'
	config.ADDITIONAL_SPACES_ALLOWED = False
	zctx = ZCtx(
		filepath,
		LLI_requirements,
		config.read(CXD + "/../cfg/pcpl_cfg.cfg"),
		config.read(CXD + "/../cfg/pcpl_itm.cfg", comment_character='%', additionnalSpacesAllowed=False),
		config.read(CXD + "/../cfg/cpl_opt.cfg"),
		debugMode = DEBUG_MODE
	)

	#precompile
	precompile(zctx)
	writeFile(output_PCPL, dreamlands.toText(zctx.pcpl.dataResult))

	#compile
	compile(zctx)
	writeFile(output_CPL, zctx.cpl.textResult)

#run main
main()

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
	if len(sys.argv) < 3:
		print("zcc: Missing arguments (filename, LLI_requirement_file).")
		exit(1)
	filepath         = sys.argv[1]
	LLI_requirements = config.read(sys.argv[2])

	#prepare output filename
	outputFilename = path_name(os.path.basename(filepath)) + ".nc"

	#z code context
	config.COMMENT_CHARACTER         = '%'
	config.ADDITIONAL_SPACES_ALLOWED = False
	zCtx = zctx(
		filepath,
		LLI_requirements,
		config.read(CXD + "/../cfg/pcpl_cfg.cfg"),
		config.read(CXD + "/../cfg/pcpl_itm.cfg", comment_character='%', additionnalSpacesAllowed=False),
		config.read(CXD + "/../cfg/cpl_opt.cfg"),
		debugMode = DEBUG_MODE
	)
	if DEBUG_MODE and not os.path.isdir("debug"):
		os.mkdir("debug")

	#precompile
	zCtx.pcpl.ZCIs = precompile(zCtx)

	#compile
	compile(zCtx)
	writeFile(outputFilename, zCtx.cpl.textResult)

#run main
main()

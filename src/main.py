#!/usr/bin/python3



# -------- IMPORTATIONS --------

#system
import os, sys
CXD  = os.path.dirname(os.path.realpath(sys.argv[0]))
pCXD = os.path.dirname(CXD)
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
P3  = 0 #global enm
C01 = 1
C02 = 2
C03 = 3
DEBUG_MODES = { #these 2 are to be global VARIABLE dataitems (static)
	P3 :False,
	C01:False,
	C02:False,
	C03:True
}
DEEP_DEBUG_MODES = {
	P3 :False,
	C01:False,
	C02:False,
	C03:True
}

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

	#args: filepath
	if len(sys.argv) < 2:
		print("zcc: Missing arguments (at least 1 required: \"filepath\").")
		exit(1)
	filepath = sys.argv[1]

	#args: LLI requirement file (optional)
	if len(sys.argv) >= 3:
		LLIRequirements = config.read(sys.argv[2])

	#default value instead
	else:
		print("zcc: No LLI requirement file given => using LLI inventory instead.")
		LLICfg = config.read(pCXD + "/cfg/LLI.cfg")

		#cfg issue
		try:
			defaultLLIRequirementsFilepath = LLICfg['PATH'] + "/cfg/inventory.cfg"
		except:
			print("zcc: No LLI path defined in cfg/LLI.cfg")
			exit(1)

		#LLI issue
		try:
			LLIRequirements = config.read(defaultLLIRequirementsFilepath)
		except:
			print("zcc: Unable to find default LLI requirement file (LLI inventory) at location: " + defaultLLIRequirementsFilepath)
			exit(1)

	#prepare output filename
	outputFilename = path_name(os.path.basename(filepath)) + ".nc"

	#z code context
	config.COMMENT_CHARACTER         = '%'
	config.ADDITIONAL_SPACES_ALLOWED = False
	zCtx = newZCtx(
		filepath,
		LLIRequirements,
		config.read(CXD + "/../cfg/pcpl_cfg.cfg"),
		config.read(CXD + "/../cfg/pcpl_itm.cfg", comment_character='%', additionnalSpacesAllowed=False),
		config.read(CXD + "/../cfg/cpl_opt.cfg"),
		debugMode     = DEBUG_MODES[P3],
		deepDebugMode = DEEP_DEBUG_MODES[P3]
	)
	if (
		True in ( list(DEBUG_MODES.values()) + list(DEEP_DEBUG_MODES.values()) )
	) and not os.path.isdir("debug"):
		os.mkdir("debug")

	#precompile
	zCtx.ZCIs = precompile(zCtx)

	#compile
	compile(zCtx, DEBUG_MODES, DEEP_DEBUG_MODES) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< debug paramaters should not be passed as parameters, they are global & variable (static)
	writeFile(outputFilename, zCtx.cpl.textResult)

#run main
main()

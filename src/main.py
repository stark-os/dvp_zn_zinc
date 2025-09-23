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






# -------- EXECUTION --------

#main
def main():

	#args: filepath
	if len(sys.argv) < 2:
		print("zcc: Missing arguments (at least 1 required: \"filepath\").")
		exit(1)
	filepath = sys.argv[1]

	#args: LLI inventory filepath (optional)
	LLIInvFilepath = ""
	if len(sys.argv) >= 3:
		LLIInvFilepath = sys.argv[2]

	#default path instead
	else:
		LLILclFilepath = pCXD + "/cfg/LLI.cfg"
		print("No LLI inventory file given")
		print("  => look for a default LLI at PATH mentionned in local " + LLILclFilepath)

		#parse local LLI cfg
		try:
			LLILclCfg = config.read(LLILclFilepath)
		except:
			print("zcc: Unable to read local LLI configuration file " + LLILclFilepath)
			exit(1)

		#local cfg missing field
		try:
			LLIInvFilepath = LLILclCfg['PATH'] + "/cfg/inventory.cfg"
		except:
			print("zcc: No LLI path defined in cfg/LLI.cfg (\"PATH\" field required).")
			exit(1)
		print("Default LLI PATH set, and found LLI at that location.")
		print("  => Using its default inventory " + LLIInvFilepath)

	#prepare output filename
	outputFilename = path_name(os.path.basename(filepath)) + ".nc"

	#z code context
	zCtx = newZCtx(
		filepath,
		LLIInvFilepath,
		config.read(CXD + "/../cfg/pcpl_cfg.cfg"),
		config.read(CXD + "/../cfg/pcpl_itm.cfg", comment_character='%', additionnalSpacesAllowed=False),
		config.read(CXD + "/../cfg/cpl_opt.cfg"),

		#debug
		dbgMode = (
			False, #INIT
			False,  #P1
			False, #P2
			False, #P3
			False, #C01
			True,  #C02
			True   #C03
		), deepDbgMode = (
			False, #INIT
			False,  #P1
			False, #P2
			False, #P3
			False, #C01
			True,  #C02
			True   #C03
		), stepByStep = True
	)

	#precompile
	zCtx.ZCIs = precompile(zCtx)

	#compile
	compile(zCtx)
	writeFile(outputFilename, zCtx.cpl.txtRes)

#run main
main()

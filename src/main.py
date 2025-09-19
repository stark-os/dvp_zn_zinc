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
DBG__INIT = 0 #global enm
DBG__P3   = 1
DBG__C01  = 2
DBG__C02  = 3
DBG__C03  = 4
DBG_MODES = { #these 2 are to be global VARIABLE dataitems (static)
	DBG__INIT:False,
	DBG__P3  :False,
	DBG__C01 :False,
	DBG__C02 :True,
	DBG__C03 :True
}
DEEP_DBG_MODES = {
	DBG__INIT:False,
	DBG__P3  :False,
	DBG__C01 :False,
	DBG__C02 :True,
	DBG__C03 :True
}






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
	config.COMMENT_CHARACTER         = '%'
	config.ADDITIONAL_SPACES_ALLOWED = False
	zCtx = newZCtx(
		filepath,
		LLIInvFilepath,
		config.read(CXD + "/../cfg/pcpl_cfg.cfg"),
		config.read(CXD + "/../cfg/pcpl_itm.cfg", comment_character='%', additionnalSpacesAllowed=False),
		config.read(CXD + "/../cfg/cpl_opt.cfg"),

		#debug
		dbgMode     = DBG_MODES[DBG__INIT],
		deepDbgMode = DEEP_DBG_MODES[DBG__INIT]
	)
	if (
		True in (
			list(DBG_MODES.values()) + list(DEEP_DBG_MODES.values())
		)
	) and not os.path.isdir("debug"):
		os.mkdir("debug")

	#precompile
	zCtx.ZCIs = precompile(zCtx)

	#compile
	compile(zCtx, DBG_MODES, DEEP_DBG_MODES) #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< debug stuff should not be passed as parameters, they are global & variable (static)
	writeFile(outputFilename, zCtx.cpl.txtRes)

#run main
main()

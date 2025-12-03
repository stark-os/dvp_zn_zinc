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






# -------- TMP --------

#tmp <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
mode = CPL__MODE_N
tgt  = CPL__TGT_SDL






# -------- EXECUTION --------

#main
def main():

	#args: filepath
	if len(sys.argv) < 2:
		print("zinc: Missing arguments (at least 1 required: \"filepath\").")
		exit(1)
	filepath = sys.argv[1]

	#prepare output filename
	name           = path_name(os.path.basename(filepath))
	outputFilename = name + ".obv"
	if tgt == CPL__TGT_SDL:
		outputFilename_FP = name + ".sdl.cfg"
	else:
		outputFilename_FP = name + ".elf.cfg"

	#z code context
	zCtx = newZCtx(
		filepath,
		config.read(CXD + "/../cfg/pcpl_cfg.cfg"),
		config.read(CXD + "/../cfg/pcpl_itm.cfg", comment_character='%', additionnalSpacesAllowed=False),
		config.read(CXD + "/../cfg/cpl_opt.cfg"),
		tgt|mode,

		#debug
		log_lvls = (
			LOG__LVL_INF, #INIT
			LOG__LVL_INF, #P1
			LOG__LVL_INF, #P2
			LOG__LVL_INF, #P3
			LOG__LVL_INF, #C01
			LOG__LVL_INF, #C02
			LOG__LVL_INF, #C03
			LOG__LVL_INF, #C04
			LOG__LVL_INF, #C05
			LOG__LVL_INF, #C06
			LOG__LVL_INF, #C07
			LOG__LVL_INF  #C08
		), stepByStep = False
	)

	#precompile
	zCtx.ZCIs = precompile(zCtx)

	#compile
	compile(zCtx)
	writeFile(outputFilename,    '\n'.join(zCtx.cpl.resObv))
	writeFile(outputFilename_FP, zCtx.cpl.resFP)

#run main
main()

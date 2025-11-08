# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/p-cpl2.py

	#user dynamic access pcpl cfg
	def checkPcplCfg(sbj, pcpl):
		for k in pcpl.cfgs.keys():

			#maximum complexity level allowed in directives
			if k == PCPL__DIRECTIVES_MAX_COMPLEXITY_KEY:
				sbj.dbg("PCPL cfg \"" + PCPL__DIRECTIVES_MAX_COMPLEXITY_KEY + "\" defined in pcpl_cfg.cfg => using it instead of the default one: " + str(PCPL__DIRECTIVES_MAX_COMPLEXITY))
				sbj.directivesMaxComplexity = str_dec_toUM(pcpl.cfgs[maxComplexityKey], 0, sys.maxsize, forbidNegative=True) #should use INT_MAX here



	#each cpl option must be defined
	def checkCplOpt(sbj, cpl_opt):
		for o in CPL_OPT__ALLOWED.keys():

			#option must be defined
			if o not in cpl_opt:
				sbj.err("Missing compilation option \"" + o + "\" in local cfg/cpl_opt.cfg.", prtLine=False, prtSubCtxs=False)

			#check value: ARCH type
			if CPL_OPT__ALLOWED[o] == CPL_OPT__VALUES__ARCH:
				if cpl_opt[o] not in ("32", "64"):
					sbj.err("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " in local cfg/cpl_opt.cfg (32 or 64 expected)")

			#check value: FILE PATH
			elif CPL_OPT__ALLOWED[o] == CPL_OPT__VALUES__FILE:
				if not os.path.isfile(cpl_opt[o]):
					sbj.err("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " in local cfg/cpl_opt.cfg (existing file path expected)")

			#check value: ON / OFF
			elif CPL_OPT__ALLOWED[o] == CPL_OPT__VALUES__ONOFF:
				if cpl_opt[o] not in ("ON", "OFF"):
					sbj.err("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " in local cfg/cpl_opt.cfg (ON or OFF expected)")

			#check value: integer
			elif CPL_OPT__ALLOWED[o] == CPL_OPT__VALUES__DIGIT:
				if not str_isConvertible_int(cpl_opt[o]):
					sbj.err("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " in local cfg/cpl_opt.cfg (integer expected)")

			#check value: root type
			elif CPL_OPT__ALLOWED[o] == CPL_OPT__VALUES__RTYPE:
				if cpl_opt[o] not in ROOT_TYPES:
					sbj.err("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " in local cfg/cpl_opt.cfg (root type expected among " + ", ".join(ROOT_TYPES) + ")")

		#check for additionnal options (not allowed)
		if len(cpl_opt) > len(CPL_OPT__ALLOWED):
			for o in cpl_opt.keys():
				if o not in CPL_OPT__ALLOWED.keys():
					sbj.err("Unknown compilation option \"" + o + "\" in local cfg/cpl_opt.cfg.")









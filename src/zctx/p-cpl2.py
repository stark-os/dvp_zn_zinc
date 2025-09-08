# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/p-cpl2.py


	#each cpl option must be defined
	def checkCplOpt(self, cpl_opt):

		#check each required option
		for o in CPL_OPT_ALLOWED.keys():

			#option must be defined
			if o not in cpl_opt:
				self.error("Missing compilation option \"" + o + "\" in configuration file cpl_opt.cfg.")

			#check value: ARCH type
			if CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__ARCH:
				if cpl_opt[o] not in ("32", "64"):
					self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (32 or 64 expected)")

			#check value: ON / OFF
			elif CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__ONOFF:
				if cpl_opt[o] not in ("ON", "OFF"):
					self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (ON or OFF expected)")

			#check value: integer
			elif CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__DIGIT:
				if not str_isConvertible_int(cpl_opt[o]):
					self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (integer expected)")

			#check value: root type
			elif CPL_OPT_ALLOWED[o] == CPL_OPT_VALUES__RTYPE:
				if cpl_opt[o] not in ROOT_TYPES:
					self.error("Invalid value \"" + cpl_opt[o] + "\" for compilation option " + o + " (root type expected among " + ", ".join(ROOT_TYPES) + ")")

		#check for additionnal options (not allowed)
		if len(cpl_opt) > len(CPL_OPT_ALLOWED):
			for o in cpl_opt.keys():
				if o not in CPL_OPT_ALLOWED.keys():
					self.error("Unknown compilation option \"" + o + "\".")




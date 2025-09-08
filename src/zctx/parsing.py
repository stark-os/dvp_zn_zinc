# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/parsing.py



	# PARSING

	#parsing shortcut relays
	def get(self):
		return self.ctx.get()

	def inc(self):
		return self.ctx.inc()

	def forward(self, step):
		return self.ctx.forward(step)



	# SUBCONTEXTS

	#file contexts return true if successfully openned (false means : file already processed => ignoring it)
	def openNewSubCtx(self, filepath):
		if not filepath.endswith(".z"):
			filepath += ".z"

		#resolve relativeness of given filepath regarding current context location
		if not filepath.startswith('/'):
			filepath = self.ctx.dirname + '/' + filepath

		#check already openned
		realNewPath = os.path.realpath(filepath)
		for c in self.imported:
			if realNewPath == c:
				self.deepDebug("Subctx \"" + realNewPath + "\" already openned once => skipping it.")
				return False

		#open new subcontext
		self.deepDebug("Opening subctx \"" + filepath + "\".")
		try:
			newCtx   = ParsingCtx(filepath, readFile(filepath))
		except FileNotFoundError:
			self.error("File " + filepath + " not found.")
		except IsADirectoryError:
			self.error("Element " + filepath + " is a directory (expected file).")

		#not already openned => add it to importations
		self.ctx = newCtx
		self.subCtxs.append(newCtx)
		self.imported.append(realNewPath)
		return True

	def closeCurrentCtx(self): #return True if no more context remains
		self.deepDebug("Closing latest subctx.")
		lst_pop(self.subCtxs)

		#no more subcontext remaining
		if lst_isEmpty(self.subCtxs):
			self.ctx = None
			self.deepDebug("No more subctx remaining.")
			return True

		#subcontexts remaining
		self.deepDebug("Back here:", printSubCtxs=True)
		self.ctx = lst_last(self.subCtxs)
		return False

	def overwriteSubCtxs(self, subCtxs):
		self.subCtxs = subCtxs
		if lst_isEmpty(subCtxs):
			self.ctx = None
		else:
			self.ctx = subCtxs[-1]








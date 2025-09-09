# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/parsing.py

# PARSING

#parsing shortcut relays
def zCtx__get(sbj):
	return sbj.ctx.get()

def zCtx__inc(sbj):
	return sbj.ctx.inc()

def zCtx__forward(sbj, step):
	return sbj.ctx.forward(step)



# SUBCONTEXTS

#file contexts return true if successfully openned (false means : file already processed => ignoring it)
def zCtx__openNewSubCtx(zCtx, filepath):
	if not filepath.endswith(".z"):
		filepath += ".z"

	#resolve relativeness of given filepath regarding current context location
	if not filepath.startswith('/'):
		filepath = zCtx.ctx.dirname + '/' + filepath

	#check already openned
	realNewPath = os.path.realpath(filepath)
	for c in zCtx.imported:
		if realNewPath == c:
			zCtx.deepDebug("Subctx \"" + realNewPath + "\" already openned once => skipping it.")
			return False

	#open new subcontext
	zCtx.deepDebug("Opening subctx \"" + filepath + "\".")
	try:
		newCtx = ParsingCtx(filepath, readFile(filepath))
	except FileNotFoundError:
		zCtx.error("File " + filepath + " not found.")
	except IsADirectoryError:
		zCtx.error("Element " + filepath + " is a directory (expected file).")

	#not already openned => add it to importations
	zCtx.ctx = newCtx
	zCtx.subCtxs.append(newCtx)
	zCtx.imported.append(realNewPath)
	return True

def zCtx__closeCurrentCtx(zCtx): #return True if no more context remains
	zCtx.deepDebug("Closing latest subctx.")
	lst_pop(zCtx.subCtxs)

	#no more subcontext remaining
	if lst_isEmpty(zCtx.subCtxs):
		zCtx.ctx = None
		zCtx.deepDebug("No more subctx remaining.")
		return True

	#subcontexts remaining
	zCtx.deepDebug("Back here:", printSubCtxs=True)
	zCtx.ctx = lst_last(zCtx.subCtxs)
	return False

def zCtx__overwriteSubCtxs(zCtx, subCtxs):
	zCtx.subCtxs = subCtxs
	if lst_isEmpty(subCtxs):
		zCtx.ctx = None
	else:
		zCtx.ctx = subCtxs[-1]








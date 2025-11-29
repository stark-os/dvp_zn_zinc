# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/parsing.py

# PARSING

#parsing shortcut relays
def zCtx__get(sbj):
	return sbj.ctx.get()

def zCtx__inc(sbj):
	return sbj.ctx.inc()

def zCtx__forward(sbj, step):
	return sbj.ctx.forward(step)

def zCtx__resetCtx(sbj, newCtx):
	sbj.ctx         = newCtx
	sbj.subCtxs[-1] = newCtx

def zCtx__reset(sbj, newText=None):
	sbj.ctx.reset(newText=newText)

def zCtx__reachedEnd(sbj):
	return sbj.ctx.reachedEnd()



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
			zCtx.dbg1("Subctx \"" + realNewPath + "\" already openned once => skipping it.")
			return False

	#open new subcontext
	zCtx.dbg1("Opening subctx \"" + filepath + "\".")
	try:
		newCtx = ParsingCtx(filepath, readFile(filepath))
	except FileNotFoundError:
		zCtx.err("File " + filepath + " not found.")
	except IsADirectoryError:
		zCtx.err("Element " + filepath + " is a directory (expected file).")

	#not already openned => add it to importations
	zCtx.ctx = newCtx
	zCtx.subCtxs.append(newCtx)
	zCtx.imported.append(realNewPath)
	return True

def zCtx__closeCurrentCtx(zCtx): #return True if no more context remains
	zCtx.dbg1("Closing latest subctx.")
	lst_pop(zCtx.subCtxs)

	#no more subcontext remaining
	if lst_isEmpty(zCtx.subCtxs):
		zCtx.ctx = None
		zCtx.dbg1("No more subctx remaining.")
		return True

	#subcontexts remaining
	zCtx.dbg1("Back here:", prtSubCtxs=True)
	zCtx.ctx = lst_last(zCtx.subCtxs)
	return False

def zCtx__overwriteSubCtxs(zCtx, subCtxs):
	zCtx.subCtxs = subCtxs
	if lst_isEmpty(subCtxs):
		zCtx.ctx = None
	else:
		zCtx.ctx = subCtxs[-1]






# ---------------- IN CODE ----------------

#read a number as raw text (similar to zctx.readName but way simpler and overall: skipping underscores!)
def readNbrAsText(ZCI, allowedCharset):
	resTxt = ZCI.get()
	ZCI.inc()

	#read until non-charset character found
	while not ZCI.reachedEnd():
		c = ZCI.get()

		#skip underscores
		if c == '_':
			ZCI.inc()
			continue

		#out of charset => stop here
		if c not in allowedCharset:
			break

		#else, add to res
		resTxt += c
		ZCI.inc()
	return resTxt






# ---------------- DBG ----------------

#debug
def prepareDbgDir():
	if not os.path.isdir("dbg"):
		os.mkdir("dbg")

def strLst_toDsp(sl):

	#get longest str to display
	maxLen = 0
	for s in sl:
		if len(s) > maxLen:
			maxLen = len(s)

	#compute optimal modulo depending on terminal width
	dspModulo = int( (Term__width()-10-len(TERM__OUTPUT_TAB))/(maxLen+3) )

	#create text list
	res = "["
	for i in range(len(sl)):
		s = sl[i]
		if i%dspModulo == 0:
			res += '\n' + TERM__OUTPUT_TAB
		res += '\"' + s + "\"," + ' '*(maxLen-len(s))
	return res + "\n]"

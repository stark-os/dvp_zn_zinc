# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/other.py

# ---------------- OTHER ----------------

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



#debug dir
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

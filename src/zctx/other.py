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


def lstAllValWithID_inScope(scope, atmID):
	res = [] #lst[vs]

	#get vals from exes first
	for e in scope.exes:
		res += lstAllValWithID_inExe(e, atmID, scope)

	#also add def vals of datItms
	for di in scope.datItms:
		if di.inited:
			if di.initVal.vdat.id == atmID:
				res.append(vs(di.initVal, scope))

	#res
	return res

def lstAllValWithID_inExes(exes, atmID, scope):
	res = [] #lst[val]

	#asg
	if e.id == ATM__ASG:
		if e.dat.src.vdat.id == atmID:
			res.append(vs(e.dat.src, scope))
		if e.dat.dst.vdat.id == atmID:
			res.append(vs(e.dat.dst, scope))

	#if
	elif e.id == ATM__STM_IF:
		if e.dat.cond.vdat.id == atmID:
			res.append(vs(e.dat.cond, scope))
		res += lstAllValWithID_inScope(e.dat.scope, atmID)

	#whi
	elif e.id == ATM__STM_WHI:
		if e.dat.iterCond.vdat.id == atmID:
			res.append(e.dat.iterCond)
		res += lstAllValWithID_inScope(e.dat.scope, atmID)

	#swi
	elif e.id == ATM__STM_SWI:
		if e.dat.tgt.vdat.id == atmID:
			res.append(e.dat.tgt)
		for c in e.dat.cases:
			if c.vdat.id == atmID:
				res.append(c)
		for s in e.dat.scopes:
			res += lstAllValWithID_inScope(s, atmID)

	#jmp
	elif e.id == ATM__JMP:
		if e.dat.retVal is not None:
			if e.dat.retVal.vdat.id == atmID:
				res.append(e.dat.retVal)

	#call (VFC)
	elif e.id == ATM__CALL:
		for p in e.dat.paramVals:
			if p.vdat.id == atmID:
				res.append(p)

	#res
	return res

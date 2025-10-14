# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/genericTools.py

# -------- TYPES RELATED TOOLS --------

#type fields
def getTypeFieldFromName(ZCI, tgtTypeID, tgtFieldName):
	tInst = ZCI.zCtx.getTypeInstanceFromID(tgtTypeID)

	#type nature check
	if tInst.dcnCommon.nature == NATURE__PRM:
		ZCIErr(ZCI, "Type " + unpfxMod(tInst.name) + " is a primitive type, cannot get fields from it.")

	#look for the given name in type fields
	for f in tInst.dcnCommon.fields:
		if f.name == tgtFieldName:
			return f
	ZCIErr(ZCI, "Type " + unpfxMod(tInst.name) + " has no field \"" + tgtFieldName + "\".")






# -------- DATA ITEMS RELATED TOOLS --------

#data items
def checkAlreadyDeclaredDatItmOrField(ZCI, di, dis):
	for other in dis:
		if other.name == di.name:
			ZCIErr(ZCI, "Data item or field with name \"" + di.name + "\" already declared.")

#get correct data item prefix depending on current ZCI scope
def getDatItmModPfxFromScope(ZCI, scope):
	if scope == ZCI.zCtx.cpl.gblScp:
		if len(ZCI.modPfx) != 0:
			return ZCI.modPfx + 'E' #global "MODULE ELEMENT"
		return "GE" #global "ELEMENT"
	return "L" #local (can only be an "ELEMENT")

def getDatItmFromScope(exactName, scope):
	for di in scope.datItms:
		if di.name == exactName:
			return di
	return None

def getGblScpFromScope(scope):
	if scope.parent is None:
		return scope
	return getGblScpFromScope(scope.parent)

#reeeeeeeeeeeally useful !!! Allows you to get a data item among those existing from the given scope, but only by giving the USER PREFIXED NAME: "^a.^b.c" => "Ma_Mb_Ec", "a" => "GEa" or "La", even working with function pointers
def getDatItmFromPfxName(pfxName, scope):
	modPfx = extractModPfx(pfxName)

	#case 1: module-related global element targetted
	if len(modPfx) != 0:
		scope   = getGblScpFromScope(scope) #no matter which scope we are currently into, using a module notation means "go take me a module-related GLOBAL element"
		rawName = str_sub(pfxName, start=len(modPfx))
		res     = getDatItmFromScope(modPfx + 'E' + rawName, scope)

		#last option: module function name
		if res is None:
			return getDatItmFromScope(modPfx + 'F' + rawName, scope)
		return res

	#case 2: non-module global element targetted
	if scope.parent is None:
		res = getDatItmFromScope("GE" + pfxName, scope) #scope can only be the global one here

		#last option: non-module function name
		if res is None:
			return getDatItmFromScope("GF" + pfxName, scope) #same thing
		return res

	#case 3: local scope element targetted
	res = getDatItmFromScope('L' + pfxName, scope)
	if res is None:
		return getDatItmFromPfxName(pfxName, scope.parent) #recursive call on higher scope
	return res






# -------- FUNCTIONS & METHODS RELATED TOOLS --------

#similar to getDatItmFromPrefixedName() but returns a NAME instead of a function
def getFctNameFromPfxName(ZCI, pfxName, methodOf=TYPE_ID__UNKNOWN):
	modPfx  = extractModPfx(pfxName)
	rawName = str_sub(pfxName, start=len(modPfx))

	#set prefix for non-module functions
	if len(modPfx) == 0:
		modPfx = "G"

	#method
	methodText = ""
	if methodOf != TYPE_ID__UNKNOWN:
		methodText = 'T' + ZCI.getTypeNameFromID(methodOf) + '_'

	#formated function name
	return modPfx + methodText + 'F' + rawName

def getFctFromName(ZCI, exactName):
	for f in ZCI.zCtx.cpl.fcts:
		if exactName == f.name:
			return f
	return None

#reaaaaaaaaaaaally useful too !!! Does 3 things together !
def checkAll_thenReadParams_thenCreateCall(ZCI, exactName, scope, cstOnly, noVFCAllowed=True):

	#check scope: calls are only allowed in non-global scope
	if scope == ZCI.zCtx.cpl.gblScp:
		ZCIErr(ZCI, "Calls are not allowed in global scope.")

	#try get function by name
	tgtFct = getFctFromName(ZCI, exactName)
	if tgtFct is None:
		ZCIErr(ZCI, "No matching function \"" + exactName + "\" found (parsing call).")

	#check return type
	if noVFCAllowed and tgtFct.retType == TYPE_ID__UNKNOWN:
		ZCIErr(ZCI, "Can't have void returning function call here (only !VFC allowed).")

	#read params
	paramVals = readValueSequence(ZCI, tgtFct.params, scope, cstOnly=cstOnly)

	#create call
	return call(exactName, paramVals, tgtFct.retType)

def listAllExistingFct(zCtx):
	nl = []
	for f in zCtx.cpl.fcts:
		nl.append(f.name)
	return strLst_toDsp(nl)






# -------- TEXT FORMAT RELATED TOOLS --------

#undouble underscores
def undblUnderscores(s):
	return s.replace("__", '_')

#unprefixing module prefixes especially
def unpfxMod(modPfx):
	if len(modPfx) == 0:
		return ""
	if modPfx[0] == 'G':
		return ""
	return "^" + str_sub(modPfx, start=1).replace("__", "%").replace("_M", ".^").replace("%",'_')[:-1] + '.'

def extractModPfx(name):
	if len(name) == 0:
		return ""
	if name[0] != 'M': #no module prefix
		return ""

	#get only module prefix from name
	modPfx       = "M"
	onUnderscore = False
	for c in name[1:]:

		#previous character was an underscore => potential end of module prefix
		if onUnderscore:
			onUnderscore = False

			#- double underscore => regular text, ignore it
			#- end of module prefix, but another one follows => still in it
			#else => definitely out of module prefix
			if c != '_' and c != 'M':
				break

		#previous character was not an underscore => we are in module prefix, sure at 100%
		elif c == '_':
			onUnderscore = True

		#in module prefix
		modPfx += c

	#count ending underscores
	uNbr      = 0
	modPfxLen = len(modPfx)
	for c in range(modPfxLen):
		if modPfx[modPfxLen-c-1] == '_':
			uNbr += 1
		else:
			break

	#error case : should never occur. It would mean we made s-thing wrong when transforming module notation into module prefix
	if uNbr%2 == 0:
		print("[INTERNAL] Invalid module prefix '" + modPfx + "' extracted from name '" + name + "' (ending with even number of underscores).")
		exit(1)
	return modPfx



#unprefixing anything <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< MAYBE MAKE IT EFFICIENT ENOUGH SO THAT WE CAN GET RID OF UNPREFIXIZEMODULE & EXTRACTMODULEPREFIX ?
def unpfxAnyName(name): #GE<name> => <name>, M<mod>_E<name> => ^<mod>.<name>, ...
	pfx = extractModPfx(name)
	return unpfxMod(pfx) + str_sub(name, len(pfx)).replace("__", '_')



#type unprefixing
def cutModPfxFromTypeName(exactName): #also return modPfx, #<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< IN Z, WE WOULD NOT HAVE TO RETURN exactName BECAUSE WE ALTER ITS INTERNAL FIELDS
	modPfx = "G"
	if exactName[0] == 'M':
		modPfx    = extractModPfx(exactName)
		exactName = str_sub(exactName, start=len(modPfx)) #here starting with dcn indicator 'U' or 'D'
	else:
		exactName = exactName[1:] #same thing
	return modPfx, exactName

def cutDcnFromTypeName(exactName):

	#keep mod pfx aside to parse correctly the rest (we will restore it at the end)
	modPfx, exactName = cutModPfxFromTypeName(exactName)

	#now, compute to cut the rest of the name with separators (which can only corresponds to dcns)
	res = ""
	onUnderscore = False
	for c in exactName:
		if onUnderscore:

			#pair of underscores => regular underscore in type name (preserve the pair!)
			if c == '_':
				onUnderscore = False
				res += "__"

			#single underscore => dcn delimiter
			else:
				break
		else:

			#found underscore => check following character
			if c == '_':
				onUnderscore = True

			#regular character => add it to name
			else:
				res += c

	#result
	if len(modPfx) == 0: #keep modPfx as it was originally
		modPfx = 'G'
	return modPfx + res

def unpfxTypeName(zCtx, exactName):

	#get base type without declinations
	undcnName = cutDcnFromTypeName(exactName)

	#get remaining type name to analyse (for declinations)
	remaining = exactName[len(undcnName)+1:] #we must skip the potential 1st underscore after undcnName if something is remaining (=> +1)

	#get modPfx
	modPfx, undcnName = cutModPfxFromTypeName(undcnName)

	#set undcnName as "undeclinated" to find its dcnDeg
	dcned = (undcnName[0] == 'D')
	#undcnName[0] = 'U' #the Z way
	undcnName    = 'U' + undcnName[1:] #the Python way
	dcnDeg       = zCtx.getTypeInstanceFromName(modPfx + undcnName).dcnCommon.dcnDeg

	#look for decinations to read inside (recursive work)
	dcnTxt = ""
	if dcnDeg != 0 and dcned and len(remaining) != 0:
		dcnTxt += '['
		for d in range(dcnDeg):
			dcnName, remaining = unpfxTypeName(zCtx, remaining)
			dcnTxt += dcnName + ','
		dcnTxt = dcnTxt[:-1] + ']'

	#result
	return (
		unpfxMod(modPfx) + undblUnderscores(undcnName[1:]) + dcnTxt,
		remaining
	)






# ---------------- OTHER ----------------

#read a number as raw text (similar to zctx.readName but simpler and overall: skipping underscores!)
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
	dspModulo = int( (Term__width()-len(TERM__OUTPUT_TAB))/(maxLen+3) )

	#create text list
	res = "["
	for i in range(len(sl)):
		s = sl[i]
		if i%dspModulo == 0:
			res += '\n' + TERM__OUTPUT_TAB
		res += '\"' + s + "\"," + ' '*(maxLen-len(s))
	return res + "\n]"

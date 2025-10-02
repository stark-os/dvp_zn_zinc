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
def checkAlreadyDeclaredDataItemOrField(ZCI, di, dis):
	for other in dis:
		if other.name == di.name:
			ZCIErr(ZCI, "Data item or field with name \"" + di.name + "\" already declared.")

#get correct data item prefix depending on current ZCI scope
def getDataItemModPfxFromScope(ZCI, scope):
	if scope == ZCI.zCtx.cpl.gblScp:
		if len(ZCI.modPfx) != 0:
			return ZCI.modPfx + 'E' #global "MODULE ELEMENT"
		return "GE" #global "ELEMENT"
	return "L" #local (can only be an "ELEMENT")

def getDataItemFromScope(exactName, scope):
	for di in scope.dataItems:
		if di.name == exactName:
			return di
	return None

def getGblScpFromScope(scope):
	if scope.parent is None:
		return scope
	return getGblScpFromScope(scope.parent)

#reeeeeeeeeeeally useful !!! Allows you to get a data item among those existing from the given scope, but only by giving the USER PREFIXED NAME: "^a.^b.c" => "Ma_Mb_Ec", "a" => "GEa" or "La", even working with function pointers
def getDataItemFromPfxName(pfxName, scope):
	modPfx = extractModPfx(pfxName)

	#case 1: module-related global element targetted
	if len(modPfx) != 0:
		scope   = getGblScpFromScope(scope) #no matter which scope we are currently into, using a module notation means "go take me a module-related GLOBAL element"
		rawName = str_sub(pfxName, start=len(modPfx))
		res     = getDataItemFromScope(modPfx + 'E' + rawName, scope)

		#last option: module function name
		if res is None:
			return getDataItemFromScope(modPfx + 'F' + rawName, scope)
		return res

	#case 2: non-module global element targetted
	if scope.parent is None:
		res = getDataItemFromScope("GE" + pfxName, scope) #scope can only be the global one here

		#last option: non-module function name
		if res is None:
			return getDataItemFromScope("GF" + pfxName, scope) #same thing
		return res

	#case 3: local scope element targetted
	res = getDataItemFromScope('L' + pfxName, scope)
	if res is None:
		return getDataItemFromPfxName(pfxName, scope.parent) #recursive call on higher scope
	return res






# -------- FUNCTIONS & METHODS RELATED TOOLS --------

#similar to getDataItemFromPrefixedName() but returns a NAME instead of a function
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
	params = readValueSequence(ZCI, tgtFct.params, scope, cstOnly=cstOnly)

	#create call
	return call(exactName, params, tgtFct.retType)






# -------- TEXT FORMAT RELATED TOOLS --------

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
	modPfx          = "M"
	foundUnderscore = False
	for c in name[1:]:

		#previous character was an underscore => potential end of module prefix
		if foundUnderscore:
			foundUnderscore = False

			#- double underscore => regular text, ignore it
			#- end of module prefix, but another one follows => still in it
			#else => definitely out of module prefix
			if c != '_' and c != 'M':
				break

		#previous character was not an underscore => we are in module prefix, sure at 100%
		elif c == '_':
			foundUnderscore = True

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
		print("[INTERNAL] Invalid module prefix '" + modPrefix + "' extracted from name '" + name + "' (ending with even number of underscores).")
		exit(1)
	return modPfx

def cutDcnFromTypeName(exactTypeName):
	rawName = exactTypeName #not affected for non-module types

	#module prefixes causes problems for next step
	hasModPfx = (exactTypeName[0] == 'M')
	if hasModPfx:
		modPfx  = extractModPfx(exactTypeName)
		rawName = str_sub(exactTypeName, start=len(modPfx)) #not exactly raw here because starting with declination indicator 'U' or 'D'

	#now, compute to cut the rest of the name with separators (which can only corresponds to declinations)
	res = ""
	onUnderscore = False
	for c in rawName:
		if onUnderscore:

			#pair of underscores => regular underscore in type name
			if c == '_':
				onUnderscore = False
				res += '_'

			#single underscore => declination delimiter
			else:
				break
		else:

			#found underscore => check following character
			if c == '_':
				onUnderscore = True

			#regular character => add it to name
			else:
				res += c

	#restore module prefix if it has been taken off
	if hasModPfx:
		res = modPfx + res
	return res



#unprefixing anything <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< MAYBE MAKE IT EFFICIENT ENOUGH SO THAT WE CAN GET RID OF UNPREFIXIZEMODULE & EXTRACTMODULEPREFIX ?
def unpfxAnyName(name): #GE<name> => <name>, M<mod>_E<name> => ^<mod>.<name>, ...
	pfx = extractModPfx(name)
	return unpfxMod(pfx) + str_sub(name, len(pfx)).replace("__", '_')

#read a number as raw text (similar to zctx.readName but simpler and overall: skipping underscores!)
def readNbrAsText(ZCI, allowedCharset):
	resultText = ZCI.get()
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

		#else, add to result
		resultText += c
		ZCI.inc()
	return resultText



#debug dir
def prepareDbgDir():
	if not os.path.isdir("debug"):
		os.mkdir("debug")














# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/independantTools.py

# -------- TEXT TOOLS --------

#unprefixing module prefixes especially
def unprefixizeModule(modulePrefix):
	if len(modulePrefix) == 0:
		return ""
	if modulePrefix[0] == 'G':
		return ""
	return "^" + str_sub(modulePrefix, start=1).replace("__", "%").replace("_M", ".^").replace("%",'_')[:-1] + '.'

def extractModulePrefix(name):
	if len(name) == 0:
		return ""
	if name[0] != 'M': #no module prefix
		return ""

	#get only module prefix from name
	modulePrefix    = "M"
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
		modulePrefix += c

	#count ending underscores
	uNbr = 0
	modulePrefix_length = len(modulePrefix)
	for c in range(modulePrefix_length):
		if modulePrefix[modulePrefix_length-c-1] == '_':
			uNbr += 1
		else:
			break

	#error case : should never occur. It would mean we made s-thing wrong when transforming module notation into module prefix
	if uNbr%2 == 0:
		print("[INTERNAL] Invalid module prefix '" + modulePrefix + "' extracted from name '" + name + "' (ending with even number of underscores).")
		exit(1)
	return modulePrefix

#unprefixing anything <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< MAYBE MAKE IT EFFICIENT ENOUGH SO THAT WE CAN GET RID OF UNPREFIXIZEMODULE & EXTRACTMODULEPREFIX ?
def unprefixizeAnyName(name): #GE<name> => <name>, M<mod>_E<name> => ^<mod>.<name>, ...
	prefix = extractModulePrefix(name)
	return unprefixizeModule(prefix) + str_sub(name, len(prefix)).replace("__", '_')

#def extractAnyPrefix()
#	return



#look for data item in given scope. WARNING! Name must be given without any prefix + module prefixes not supported !
def getDataItem(name, scope):
	fullName = 'L' + name

	#look for dataItem in current scope first (considering it local)
	for di in scope.dataItems:
		if fullName == di.name:
			return di

	#not found and no parent scope => considering it global => look for it in global elements
	if scope.parent is None:
		fullName = "GE" + name
		for di in scope.dataItems:
			if fullName == di.name:
				return di

	#not found but having a parent scope => look for it in its parent
	else:
		return getDataItem(name, scope.parent)

	#not found even after scanning global scope => unknown
	return None



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












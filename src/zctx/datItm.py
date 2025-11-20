# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/datItm.py

# ---------------- DATA ITEMS RELATED TOOLS ----------------

#data items
def alreadyDclDatItmOrField(di, dis):
	for other in dis:
		if other.name == di.name:
			return True
	return False

def checkAlreadyDclDatItmOrField(ZCI, di, dis):
	if alreadyDclDatItmOrField(di, dis):
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

def getDatItmFromScopeAndParents(modPfx, rawName, scope):

	#in mod => gbl scope only
	if modPfx.startswith('M'):
		return getDatItmFromScope(modPfx + 'E' + rawName, getGblScpFromScope(scope))

	#global scope => use "G" pfx and don't look at parents
	if scope.parent is None:
		return getDatItmFromScope("GE" + rawName, scope)

	#local scope => use "L" prefix" and look in parent
	else:
		lclName = 'L' + rawName
		di      = getDatItmFromScope(lclName, scope)
		if di is not None:
			return di

		#look in parent
		return getDatItmFromScopeAndParents("", rawName, scope.parent) #modPfx given doe not matter

def listDatItmNamesAvailable(scope):
	l = []

	#add lcl scopes first
	while scope.parent is not None:
		for di in scope.datItms:
			l.append("(lcl) " + undblUnderscores(di.name[1:]))
		scope = scope.parent

	#add gbl scope then
	for di in scope.datItms:
		modPfx = extractModPfx(di.name)
		if len(modPfx) == 0:
			l.append("(gbl) " + undblUnderscores(di.name[2:]))
		else:
			l.append(unpfxMod(modPfx) + undblUnderscores(str_sub(di.name, start=len(modPfx)+1)) )

	#as output
	return strLst_toDsp(l)

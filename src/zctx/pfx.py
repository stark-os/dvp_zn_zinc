# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/pfx.py

# ---------------- TEXT FORMAT RELATED TOOLS ----------------

#double underscores
def dblUnderscores(s):
	return s.replace('_', "__")

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

	#enms
	if exactName[1] == 'N':
		return (undblUnderscores(exactName[2:]), "")

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
	print("PPPPPPPPPPPPPPPPPPPPPPP[" + modPfx +'|'+ undcnName + "]")
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

def unpfxOpeName(zCtx, o):
	txt = "operator " + str_sub(o.name, start=1, stop=3) + '('
	for p in o.params:
		txt += unpfxTypeName(zCtx, zCtx.getTypeNameFromID(p.Type)) + ','
	return txt + ')'


def unpfxFctName(zCtx, f):

	#operator
	if f.name[0] == 'O':
		return unpfxOpeName(zCtx, f)

	#in/out mod
	fModPfx = unpfxMod(f.name)
	if len(fModPfx) == 0:
		rawName = str_sub(f.name, start=2)
	else:
		rawName = str_sub(f.name, start=len(fModPfx)+1)

	#method type also
	methodTypePfx = ""
	if f.methodOf != TYPE_ID__UNKNOWN:
		methodTypePfx = unpfxTypeName(rawName)
		rawName       = str_sub(rawName, start=len(methodTypePfx))
	return fModPfx + methodTypePfx + rawName

def unpfxDatItm(exactName):

	#"L" lcl
	if exactName.startswith('L'):
		return ("", exactName[1:])

	#"GE" gbl elm
	if exactName.startswith('G'):
		return ("", exactName[2:])

	#"Mmod_E"
	modPfx = extractModPfx(exactName)
	return (modPfx, str_sub(exactName, start=len(modPfx)+1))

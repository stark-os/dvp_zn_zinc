# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/type.py

# -------- TYPE RELATED TOOLS --------

	#access using zCtx
	def getTypeInstanceFromID(sbj, id):
		if id >= 0 and id < len(sbj.cpl.types):
			return sbj.cpl.types[id]
		return None

	def getTypeIDFromName(sbj, name):
		for t in range(len(sbj.cpl.types)):
			if sbj.cpl.types[t].name == name:
				return t
		return TYPE_ID__UNKNOWN

	def getTypeNameFromID(sbj, id):
		i = sbj.getTypeInstanceFromID(id)
		if i is None:
			return "<void>"
		return i.name



	#check something in declinations
	def checkIDRecursivelyInType(sbj, tID, tgtID):
		if tID == tgtID:
			return True
		dcns = sbj.getTypeInstanceFromID(tID).dcns
		if dcns is not None:
			for d in dcns:
				if sbj.checkIDRecursivelyInType(d, tgtID):
					return True
		return False



	#operator matching
	def listAllOperatorAlternatives(sbj, opeTrigram):
		l = []
		for f in sbj.cpl.fcts:
			if f.name.startswith('O' + opeTrigram):
				l.append(f)
		return l








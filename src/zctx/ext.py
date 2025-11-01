# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ext.py

	# ---------------- EXT RESOURCES ----------------

	#types
	def loadExtType(sbj, extFPPath, info):
		if len(info) < 1:
			sbj.err("Missing nature (p/s/e) for type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)
		if len(info) < 2:
			sbj.err("Missing declination degree for type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#check dcnDeg
		dcnDegTxt = info[1]
		for c in dcnDegTxt:
			if c not in string.digits:
				sbj.err("Invalid character '" + c + "' in declination degree for type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#compute it
		dcnDeg  = 0
		lastIdx = len(dcnDegTxt)-1
		for d in range(len(dcnDegTxt)):
            dcnDeg += chr_halfHex_toS8(dcnDegTxt[d]) * (10**(lastIdx-d))

		#prepare new type
		t     = sbj.cpl.newTyp(name, dcnDeg, isPub=True)
		tInst = sbj.getTypeInstanceFromID(t)

		#case 1: prm
		nat = 0
		if info[0] == 'p':
			tInst.dcnCommon.nature = NATURE__PRM

			#parent type must be given
			if len(info) < 3:
				sbj.err("Missing parent to primitive type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)
			parentID = sbj.getTypeIDFromName(info[2])
			if parentID == TYPE_ID__UNKNOWN:
				sbj.err("Unable to find parent type " + info[2] + " for primitive type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

			#relevant prm data
			tInst.dcnCommon.size   = sbj.getTypeInstanceFromID(parentID).dcnCommon.size
			tInst.dcnCommon.parent = parentID

		#case 2: stc
		elif info[0] == 's':
			tInst.dcnCommon.nature = NATURE__STC
			tInst.dcnCommon.fields = []

			#as long as we have fields to read
			remainingLen = len(info) - 2
			i            = 0
			while i < remainingLen:

				#field type
				typeName = info[2+i]
				typeID   = sbj.getTypeIDFromName(typeName)
				if typeID == TYPE_ID__UNKNOWN:
					sbj.err("Unable to find field type \"" + typeName + "\" in structure type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

				#missing field name
				if i+1 == remainingLen:
					sbj.err("Missing name associated to field type " + typeName + " in structure type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

				#field name
				name = info[3+i]
				for c in name:
					if c not in DEFAULT_NAME_CHARSET:
						sbj.err("Invalid character '" + c + "' in field name \"" + name + "\" in structure type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

				#add field
				tInst.dcnCommon.fields.append( datItm(typeID, name, False, None) )
				i += 2

			#compute size
			tInst.computeStcSize(sbj.cpl.types)

		#case 3: enm
		elif info[0] == 'e':
			tInst.dcnCommon.nature = NATURE__ENM
			tInst.dcnCommon.fields = []

			#as long as we have fields to read
			remainingLen = len(info) - 2
			i            = 0
			while i < remainingLen:
				fName = info[2+i]
				for c in fName:
					if c not in DEFAULT_NAME_CHARSET:
						sbj.err("Invalid character '" + c + "' in field name \"" + fName + "\" in structure type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

				#add field
				tInst.dcnCommon.fields.append( datItm(TYPE_ID__UNKNOWN, fName, False, None) )
				i += 1

			#compute fields sizes
			itmType = setEnmFieldsType(sbj, tInst.dcnCommon.fields)

			#remaining enm info
			tInst.dcnCommon.size   = sbj.getTypeInstanceFromID(itmType).dcnCommon.size
			tInst.dcnCommon.parent = itmType

		#unknown
		else:
			sbj.err("Invalid nature prefix '" + info[0] + "' for type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#set res as ext resource
		tInst.dcnCommon.ext = True



	#data items
	def loadExtDatItm(sbj, extFPPath, info):
		if len(info) < 1:
			sbj.err("Missing type for data item " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)
		if len(info) < 2:
			sbj.err("Missing name for data item " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#datItm type
		typeID = sbj.getTypeIDFromName(info[0])
		if typeID == TYPE_ID__UNKNOWN:
			sbj.err("Unable to find type " + info[0] + " for data item type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#datItm name
		DIName = info[1]
		for c in DIName:
			if c not in DEFAULT_NAME_CHARSET:
				sbj.err("Invalid character '" + c + "' in data item name \"" + DIName + "\" in structure type " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#create ext datItm
		di     = datItm(typeID, DIName, False, None)
		di.ext = True

		#add it to gbl scp
		sbj.cpl.gblScp.datItms.append(di)



	#fct
	def loadExtFct(sbj, extFPPath, name, info):
		if len(info) < 1:
			sbj.err("Missing return type for function " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#read params given
		retType = TYPE_ID__UNKNOWN
		params  = [] #lst[datItm]
		for i in range(len(info)):

			#get type ID (should be a root type if no other default type is loaded yet)
			tID = sbj.getTypeIDFromName(info[i])

			#"void" keyword is allowed, but every other undefined type must raise an error
			if tID == TYPE_ID__UNKNOWN and info[i] != "void":
				sbj.err("Unable to find type " + info[i] + " as parameter for function " + name + " in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

			#retType
			if i == 0:
				retType = tID

			#params
			else:
				if tID == TYPE_ID__UNKNOWN:
					sbj.err("Cannot have \"void\" as parameter type for function " + name + " (only allowed in return type), in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)
				params.append( datItm(tID, str(DEFAULT_NAME_CHARSET[i]), False, None) )

		#create ext fct
		f = newFct(name, retType, params, sbj.cpl.gblScp)
		f.ext = True

		#add fct
		sbj.cpl.fcts.append(f)



	#load LLI types, datItms & functions
	def loadExtFP(sbj, extFPPath):
		sbj.deepDbg("Loading ext fp file " + extFPPath)

		#read core fingerprint
		try:
			fp = config.read(extFPPath)
		except:
			sbj.err("Problem while extracting configuration from fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#for entry
		for name in fp.keys():
			id   = name[0]
			name = name[1:]
			info = fp[name].split(',')

			#check info element emptyness
			for i in range(len(info)):
				info[i] = info[i].strip()
				if len(info[i]) == 0:
					sbj.err("Got an empty information field associated to key \"" + name + "\" in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

			#load into zCtx
			if id == 't':
				sbj.loadExtType(extFPPath, name, info)
			elif id == 'f':
				sbj.loadExtFct(extFPPath, name, info)
			elif id == 'd':
				sbj.loadExtDatItm(extFPPath, name, info)
			else:
				sbj.err("Invalid start character '" + id + "' for key \"" + name + "\" in fingerprint file " + extFPPath, prtSubCtxs=False, prtLine=False)

		#debug
		sbj.deepDbg("Ext fp file " + extFPPath + " loaded.")

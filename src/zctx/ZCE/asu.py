# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ext.py

	# ---------------- EXT RESOURCES ----------------

	#types
	def loadExtAsuType(sbj, extAsuPath, name, info, isPub):
		if len(info) < 1:
			sbj.err("Missing nature (p/s/e) for type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
		if len(info) < 2:
			sbj.err("Missing declination degree for type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#check dcnDeg
		dcnDegTxt = info[1]
		for c in dcnDegTxt:
			if c not in string.digits:
				sbj.err("Invalid character '" + c + "' in declination degree for type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#compute it
		dcnDeg  = 0
		lastIdx = len(dcnDegTxt)-1
		for d in range(len(dcnDegTxt)):
			dcnDeg += chr_halfHex_toS8(dcnDegTxt[d]) * (10**(lastIdx-d))

		#prepare new type
		t     = sbj.cpl.newTyp(name, dcnDeg, isPub=True)
		tInst = sbj.getTypeInstanceFromID(t)



		#case 1: type copy (child)
		nat = 0
		if info[0] == 'c':

			#parent type must be given
			if len(info) < 3:
				sbj.err("Missing parent to child type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
			parentID = sbj.getTypeIDFromName(info[2])
			if parentID == TYPE_ID__UNKNOWN:
				sbj.err("Unable to find parent type " + info[2] + " for child type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

			#relevant parent data
			pInst                  = sbj.getTypeInstanceFromID(parentID)
			tInst.dcnCommon.size   = pInst.dcnCommon.size
			tInst.dcnCommon.nature = pInst.dcnCommon.nature
			tInst.dcnCommon.fields = pInst.dcnCommon.fields
			tInst.parent           = parentID



		#case 2: stc
		elif info[0] == 's':
			tInst.dcnCommon.nature = NATURE__STC
			tInst.dcnCommon.fields = []

			#as long as we have fields to read
			for i in range(len(info) - 2):
				fieldTxt = info[2+i]

				#parse "fieldTypeName:fieldName" <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< STDZ MUST PROVIDE A FCT TO SPLIT STR SAFELY WITH EXPLICIT ERR LIKE THIS .splitByChr_strict(s, c, len=2, nonEmpty=True)
				cIdx = str_findFirstChr(fieldTxt, ':')
				if cIdx == -1:
					sbj.err("Missing colon separator ':' in field definition of structure type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
				if cIdx == 0:
					sbj.err("Empty type name given in field definition of structure type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
				if cIdx == len(fieldTxt)-1:
					sbj.err("Empty name given in field definition of structure type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
				if str_findLastChr(fieldTxt, ':') != cIdx:
					sbj.err("Empty name given in field definition of structure type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
				typeName = str_sub(fieldTxt, stop=cIdx-1)
				name     = str_sub(fieldTxt, start=cIdx+1)

				#field type
				typeID = sbj.getTypeIDFromName(typeName)
				if typeID == TYPE_ID__UNKNOWN:
					sbj.err("Unable to find field type \"" + typeName + "\" of structure type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

				#field name
				for c in name:
					if c not in DEFAULT_NAME_CHARSET:
						sbj.err("Invalid character '" + c + "' in field name \"" + name + "\" of structure type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

				#add field
				tInst.dcnCommon.fields.append( datItm(typeID, name, False, None) )

			#compute size
			tInst.computeStcSize(sbj.cpl)



		#case 3: enm
		elif info[0] == 'e':
			tInst.dcnCommon.nature = NATURE__ENM
			tInst.dcnCommon.fields = []

			#as long as we have fields to read
			for i in range(len(info) - 2):
				fName = info[2+i]
				for c in fName:
					if c not in DEFAULT_NAME_CHARSET:
						sbj.err("Invalid character '" + c + "' in field name \"" + fName + "\" of enumerate type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

				#add field
				tInst.dcnCommon.fields.append( datItm(TYPE_ID__UNKNOWN, fName, False, None) )

			#compute fields sizes
			itmType = setEnmFieldsType(sbj, tInst.dcnCommon.fields)

			#remaining enm info
			tInst.dcnCommon.size = sbj.getTypeInstanceFromID(itmType).dcnCommon.size
			tInst.parent         = itmType



		#case 4: dcn of an existing type
		elif info[0] == 'd':

			#src type must be given
			if len(info) < 3:
				sbj.err("Missing source type for declinated type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
			srcTypeID = sbj.getTypeIDFromName(info[2])
			if srcTypeID == TYPE_ID__UNKNOWN:
				sbj.err("Unable to find source type " + info[2] + " for declinated type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

			#share dcnCommon
			srcTypeInst     = sbj.getTypeInstanceFromID(srcTypeID)
			tInst.dcnCommon = srcTypeInst.dcnCommon

			#must have the same share access
			if isPub != srcTypeInst.dcnCommon.isPub:
				sbj.err("Got different share access between declinated type " + name + " and its source type, in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

			#check how many dcns follows
			dcnsToRead = len(info) - 3
			if dcnsToRead != dcnDeg:
				sbj.err("Got inexact number of declinations following declinated type " + name + " (" + str(dcnDeg) + " required, got " + str(dcnsToRead) + "), in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

			#read & store them
			for i in range(dcnDeg):
				typeName = info[3+i]
				typeID   = sbj.getTypeIDFromName(typeName)
				if typeID == TYPE_ID__UNKNOWN:
					sbj.err("Unable to find type \"" + typeName + "\" in declinations of declinated type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

				#add dcn
				tInst.dcns.append(typeID)



		#unknown
		else:
			sbj.err("Invalid nature prefix '" + info[0] + "' for type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#set res as ext resource
		tInst.dcnCommon.ext   = True
		tInst.dcnCommon.isPub = isPub



	#data items
	def loadExtAsuDatItm(sbj, extAsuPath, name, info, isPub):
		if len(info) < 1:
			sbj.err("Missing type for data item " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#datItm type
		typeID = sbj.getTypeIDFromName(info[0])
		if typeID == TYPE_ID__UNKNOWN:
			sbj.err("Unable to find type " + info[0] + " for data item type " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#datItm name
		for c in name:
			if c not in DEFAULT_NAME_CHARSET:
				sbj.err("Invalid character '" + c + "' in data item name \"" + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#create ext datItm
		di       = datItm(typeID, name, False, None)
		di.ext   = True
		di.isPub = isPub

		#add it to gbl scp
		sbj.cpl.gblScp.datItms.append(di)



	#fct
	def loadExtAsuFct(sbj, extAsuPath, name, info, isPub):
		if len(info) < 1:
			sbj.err("Missing return type for function " + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#fct name
		for c in name:
			if c not in DEFAULT_NAME_CHARSET:
				sbj.err("Invalid character '" + c + "' in function name \"" + name + ", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#read params given
		retType = TYPE_ID__UNKNOWN
		params  = [] #lst[datItm]
		for i in range(len(info)):

			#"void" keyword is allowed, but every other undefined type must raise an error
			if info[i] == "void":
				tID = TYPE_ID__UNKNOWN
			else:
				tID = sbj.getTypeIDFromName(info[i])

			#retType
			if i == 0:
				retType = tID

			#params
			else:
				if tID == TYPE_ID__UNKNOWN:
					sbj.err("Cannot have \"void\" as parameter type for function " + name + " (only allowed in return type), in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
				params.append( datItm(tID, "Lp" + str(i), False, None) )

		#create ext fct
		f       = newFct(name, retType, params, sbj.cpl.gblScp)
		f.ext   = True
		f.isPub = isPub

		#add fct
		sbj.cpl.fcts.append(f)



	#load external assumed types, datItms & functions
	def loadExtAsu(sbj, extAsuPath):
		sbj.dbg1("Loading ext asu file " + extAsuPath)

		#read file
		try:
			ea = config.read(extAsuPath)
		except:
			sbj.err("Problem while extracting configuration from external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#for each entry
		for name in ea.keys():
			if len(name) < 3:
				sbj.err("Key \"" + name + "\" is too short (at least 3 chr required, got " + str(len(name)) + "), in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)
			u_r  = name[0]
			id   = name[1]
			info = ea[name].split(',')
			name = name[2:]

			#check pub/prv indicator
			if u_r == 'u':
				isPub = True
			if u_r == 'r':
				isPub = False
			else:
				sbj.err("Key \"" + name + "\" has invalid sharing indicator '" + u_r + "' (only 'u'/'r' allowed), in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

			#check info element emptyness
			for i in range(len(info)):
				info[i] = info[i].strip()
				if len(info[i]) == 0:
					sbj.err("Got an empty information field associated to key \"" + name + "\", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

			#load into zCtx
			if id == 't':
				sbj.loadExtAsuType(extAsuPath, name, info, isPub)
			elif id == 'f':
				sbj.loadExtAsuFct(extAsuPath, name, info, isPub)
			elif id == 'd':
				sbj.loadExtAsuDatItm(extAsuPath, name, info, isPub)
			else:
				sbj.err("Invalid start character '" + id + "' for key \"" + name + "\", in external assumed code addition file " + extAsuPath, prtSubCtxs=False, prtLine=False)

		#debug
		sbj.dbg1("Ext asu file " + extAsuPath + " loaded.")

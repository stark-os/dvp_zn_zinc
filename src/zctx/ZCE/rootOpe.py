# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ZCE/rootOpe.py

# ---------------- ROOT TYPE OPES ----------------

#load root types ope
def loadGivenRootPrmOpe(zCtx, opeHeader, tgtTypeIDs):
	name      = opeHeader[:]
	params    = [] #lst[datItm]
	paramArgs = [] #lst[str], for obvExes
	retTypeID = tgtTypeIDs[0]

	#for each type tgted
	biggestSz = 0
	for t in range(len(tgtTypeIDs)):
		tID   = tgtTypeIDs[t]
		tInst = zCtx.getTypeInstanceFromID(tID)

		#update biggest sz
		if tInst.dcnCommon.size > biggestSz:
			biggestSz = tInst.dcnCommon.size

		#include type in name & params
		name += '_' + tInst.name
		pName = "Lp" + str(t)
		p     = datItm(tID, pName, False, None)
		params.append(p)
		paramArgs.append("__" + pName + "+0000")

	#combination already made => skip it
	for f in zCtx.cpl.fcts:
		if f.name == name:
			zCtx.int("Root operator " + name + " is generated twice.")

	#create fct
	f       = newFct(name, tgtTypeIDs[0], params, zCtx.cpl.gblScp)
	f.isPub = False

	#fct datItms
	for p in params:
		f.scope.datItms.append(p)

	#fct exes: "ope params" (obv exe), "ret p1"
	f.scope.exes.append(atm(
		ATM__OBVEXE,
		obvExe(opeHeader[1:], 8*biggestSz, paramArgs, OBV__BEGBLANKS_FCT)
	))
	f.scope.exes.append(atm(
		ATM__JMP,
		jmp(JMP__RET, retVal=val(
			retTypeID,
			atm(ATM__DATITM, params[0]),
			False
		))
	))
	return f

def loadGivenRootPrmOpes(zCtx, tgtTypeIDs, opeHeaders):
	for opeHeader in opeHeaders:
		for t1 in tgtTypeIDs:

			#mono-operand
			if opeHeader[1:] in MONO_OPERAND_NAMES:
				zCtx.cpl.fcts.append( loadGivenRootPrmOpe(zCtx, opeHeader, [t1]) )

			#2-operand
			for t2 in tgtTypeIDs:
				zCtx.cpl.fcts.append( loadGivenRootPrmOpe(zCtx, opeHeader, [t1,t2]) )

def loadRootPrmOpes(zCtx):

	#int
	loadGivenRootPrmOpes(zCtx, zCtx.intTypes, ROOT_PRM_OPES_INT)

	#flt
	for f in zCtx.fltTypes:
		loadGivenRootPrmOpes(zCtx, [f], ROOT_PRM_OPES_FLT)

	#bol
	loadGivenRootPrmOpes(zCtx, [zCtx.TYPE_ID__BOL], ROOT_PRM_OPES_BOL)



#ref
def loadRefOpes(zCtx):
	refTypeInst    = zCtx.getTypeInstanceFromID(zCtx.refType)
	refTypeObvSize = 8 * refTypeInst.dcnCommon.size
	archTxt        = str(refTypeObvSize)

	#prepare some params
	p1 = datItm(TYPE_ID__UNKNOWN, "Lp1", False, None)
	p2 = datItm(TYPE_ID__UNKNOWN, "Lp2", False, None)
	p3 = datItm(TYPE_ID__UNKNOWN, "Lp3", False, None)



	#STEP 1: (DCN REF, ROOT INT)

	#for each root int prm given as idx
	for idxType in zCtx.intTypes:
		idxTypeName = zCtx.getTypeNameFromID(idxType)

		#for each ref[rootType]
		for dcnType in zCtx.rootTypes:

			#size
			dcnTypeInst    = zCtx.getTypeInstanceFromID(dcnType)
			dcnTypeObvSize = 8 * dcnTypeInst.dcnCommon.size

			#create dcned ref type ref[rootType]
			dcnedRefType            = zCtx.cpl.newTyp("GDref_" + dcnTypeInst.name, dcnCommon=refTypeInst.dcnCommon)
			dcnedRefTypeInst        = zCtx.getTypeInstanceFromID(dcnedRefType)
			dcnedRefTypeInst.dcns   = [dcnType]
			dcnedRefTypeInst.parent = zCtx.refType

			#params
			p1.Type = dcnedRefType
			p2.Type = idxType
			p3.Type = dcnTypeInst.name
			p1Val   = val(dcnedRefType, atm(ATM__DATITM, p1), False)
			p2Val   = val(idxType,      atm(ATM__DATITM, p2), False)



			#STEP 1.1: BAD

			#create ope "bad(ref p1, idxType p2)"
			ope       = newFct("Obad_GUref_" + idxTypeName, dcnedRefType, [p1, p2], zCtx.cpl.gblScp)
			ope.isPub = False

			#datItms
			ope.scope.datItms.append(p1)
			ope.scope.datItms.append(p2)

			#opes exes: "ret bad(p1,p2) //for s32/64"
			ope.scope.exes.append(atm(
				ATM__JMP,
				jmp(JMP__RET, retVal=val(
					dcnedRefType,
					atm(ATM__CALL, call(
						"Obad_GUs" + archTxt + "_GUs" + archTxt,
						[p1Val, p2Val],
						dcnedRefType
					)),
					False
				))
			))

			#add it
			zCtx.cpl.fcts.append(ope)



			#STEP 1.2: BSU

			#create ope "bsu(ref p1, idxType p2)"
			ope       = newFct("Obsu_GUref_" + idxTypeName, dcnedRefType, [p1, p2], zCtx.cpl.gblScp)
			ope.isPub = False

			#datItms
			ope.scope.datItms.append(p1)
			ope.scope.datItms.append(p2)

			#opes exes: "ret bsu(p1,p2) //for s32/64"
			ope.scope.exes.append(atm(
				ATM__JMP,
				jmp(JMP__RET, retVal=val(
					dcnedRefType,
					atm(ATM__CALL, call(
						"Obad_GUs" + archTxt + "_GUs" + archTxt,
						[p1Val, p2Val],
						dcnedRefType
					)),
					False
				))
			))

			#add it
			zCtx.cpl.fcts.append(ope)



			#STEP 1.3: IIN

			#create ope "iin(ref[rootType] p1, smax p2)"
			ope = newFct(
				"Oiin_GDref_" + dcnTypeInst.name + '_' + idxTypeName,
				dcnType,
				[p1, p2],
				zCtx.cpl.gblScp
			)
			ope.isPub = False

			#datItms
			ope.scope.datItms.append(p1)
			ope.scope.datItms.append(p2)
			ope.scope.datItms.append(p3) #p3 is not a param here but a dcl datItm used for storing res

			#opes exes: "bad #ref p1 p2" (obv exe), "a2d #dcnType p1 p3" (obv exe), "ret p3"
			ope.scope.exes.append(atm(
				ATM__OBVEXE,
				obvExe("bad", refTypeObvSize, ["__Lp1+0000", "__Lp2+0000"], OBV__BEGBLANKS_FCT)
			))
			ope.scope.exes.append(atm(
				ATM__OBVEXE,
				obvExe("a2d", dcnTypeObvSize, ["__Lp1+0000", "__Lp3+0000"], OBV__BEGBLANKS_FCT)
			))
			ope.scope.exes.append(atm(
				ATM__JMP,
				jmp(JMP__RET, retVal=val(
					dcnType,
					atm(ATM__DATITM, p3),
					False
				))
			))

			#add it
			zCtx.cpl.fcts.append(ope)



			#STEP 1.4: IIA

			#create ope "iia(ref[rootType] p1, smax p2, rootType p3)"
			ope = newFct(
				"Oiia_GDref_" + dcnTypeInst.name + '_' + idxTypeName + '_' + dcnTypeInst.name,
				TYPE_ID__UNKNOWN,
				[p1, p2, p3],
				zCtx.cpl.gblScp
			)
			ope.isPub = False

			#datItms
			ope.scope.datItms.append(p1)
			ope.scope.datItms.append(p2)
			ope.scope.datItms.append(p3)

			#opes exes: "bad #ref p1 p2" (obv exe), "d2a #dcnType p3 p1" (obv exe)
			ope.scope.exes.append(atm(
				ATM__OBVEXE,
				obvExe("bad", refTypeObvSize, ["__Lp1+0000", "__Lp2+0000"], OBV__BEGBLANKS_FCT)
			))
			ope.scope.exes.append(atm(
				ATM__OBVEXE,
				obvExe("d2a", dcnTypeObvSize, ["__Lp3+0000", "__Lp1+0000"], OBV__BEGBLANKS_FCT)
			))

			#add it
			zCtx.cpl.fcts.append(ope)



	#STEP 2: (UNDCN REF, UNDCN REF)

	#params
	p1.Type = zCtx.refType
	p2.Type = zCtx.refType
	p1Val   = val(zCtx.refType, atm(ATM__DATITM, p1), False)
	p2Val   = val(zCtx.refType, atm(ATM__DATITM, p2), False)



	#STEP 2.1: CEQ

	#create ope "ceq(ref p1, ref p2)"
	ope = newFct("Oceq_GUref_GUref", zCtx.TYPE_ID__BOL, [p1, p2], zCtx.cpl.gblScp)
	ope.isPub = False

	#datItms
	ope.scope.datItms.append(p1)
	ope.scope.datItms.append(p2)

	#opes exes: "ret ceq(p1,p2) //for s32/64"
	ope.scope.exes.append(atm(
		ATM__JMP,
		jmp(JMP__RET, retVal=val(
			zCtx.TYPE_ID__BOL,
			atm(ATM__CALL, call(
				"Oceq_GUs" + archTxt + "_GUs" + archTxt,
				[p1Val, p2Val],
				zCtx.TYPE_ID__BOL
			)),
			False
		))
	))

	#add it
	zCtx.cpl.fcts.append(ope)



	#STEP 2.2: CNE

	#create ope "cne(ref p1, ref p2)"
	ope = newFct("Ocne_GUref_GUref", zCtx.TYPE_ID__BOL, [p1, p2], zCtx.cpl.gblScp)
	ope.isPub = False

	#datItms
	ope.scope.datItms.append(p1)
	ope.scope.datItms.append(p2)

	#opes exes: "ret cne(p1,p2) //for s32/64"
	ope.scope.exes.append(atm(
		ATM__JMP,
		jmp(JMP__RET, retVal=val(
			zCtx.TYPE_ID__BOL,
			atm(ATM__CALL, call(
				"Ocne_GUs" + archTxt + "_GUs" + archTxt,
				[p1Val, p2Val],
				zCtx.TYPE_ID__BOL
			)),
			False
		))
	))

	#add it
	zCtx.cpl.fcts.append(ope)

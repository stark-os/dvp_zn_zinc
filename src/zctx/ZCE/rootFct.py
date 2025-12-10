# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/ZCE/fct.py

# -------- ROOT TYPES FCTS --------

#root prm conversions
def loadConvertFcts(zCtx):
	tgtTypes = zCtx.fltTypes + [zCtx.smaxType]

	#each combination
	for t1 in tgtTypes:
		for t2 in tgtTypes:
			if t1 == t2:
				continue

			#res sz
			t2Inst    = zCtx.getTypeInstanceFromID(t2)
			t2ObvSize = 8 * t2Inst.dcnCommon.size

			#names
			t1Name = zCtx.getTypeNameFromID(t1)[2:]
			t2Name = t2Inst.name[2:]

			#params
			p1 = datItm(t1, "Lp1", False, None)

			#create fct
			f = newFct("MConvert_F" + t1Name + "__to__" + t2Name, t2, [p1], zCtx.cpl.gblScp)
			f.isPub = False

			#fct datItms
			f.scope.datItms.append(p1)

			#fct exes: "cvt p1" (obv exe), "ret p1"
			f.scope.exes.append(atm(
				ATM__OBVEXE,
				obvExe("cvt" + t1Name + '_' + t2Name, t2ObvSize, ["__Lp1+0000"], OBV__BEGBLANKS_FCT)
			))
			f.scope.exes.append(atm(
				ATM__JMP,
				jmp(JMP__RET, retVal=val(
					t2,
					atm(ATM__DATITM, p1),
					False
				))
			))

			#add fct
			zCtx.cpl.fcts.append(f)

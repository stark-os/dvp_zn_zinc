# -------- TOOLS --------

#create combination list of degree N dynamically !WARNING: Pretty high complexity !
def Combinations__addDegree(curCombinations, additionnalList):
	combinationsNbr = len(curCombinations)
	if combinationsNbr == 0:
		initialCombinationDegree = 0
	else:
		initialCombinationDegree = len(curCombinations[0])

	#for each element to add
	for ae in range(len(additionnalList)):

		#adding an extra copy of itself for the new additionnal element to include (not needed at start)
		if ae != 0:
			for c in range(combinationsNbr):
				l = []
				for e in range(initialCombinationDegree): #!WARNING: This is a CUSTOM COPY ! We copy initial combinations PARTIALLY !
					l.append(curCombinations[c][e])
				curCombinations.append(l)

		#adding cur additionnal element to each newly copied combination
		for c in range(combinationsNbr):
			curCombinations[ae * combinationsNbr + c].append(additionnalList[ae])



#get combinations of a matrix of individuals all together
def Combinations__makeAll(individualsMatrix):
	collectiveCombinations = []
	if len(individualsMatrix) > 0:

		#create first combinations with degree 1
		for e in individualsMatrix[0]:
			collectiveCombinations.append([e])

		#add degrees one after another
		for other in range(len(individualsMatrix)-1):
			Combinations__addDegree(collectiveCombinations, individualsMatrix[other+1])

	#result
	return collectiveCombinations

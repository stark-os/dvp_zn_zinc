#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.stdpy import *
import string

#internal
from zctx import *






# -------- DECLARATIONS --------

#operations supported <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< ONLY len=1 SUPPORTED FOR THE MOMENT
PCPL__ATH__OPERATORS      = ("-", "+", "*", "/", "&", "|", "^") #, "**", "<<", ">>", "<<|", "|>>", "<<-", "->>")
PCPL__ATH__OPERATOR_RANKS = (
	('*','/','&','|','^'), #priority: 1
	('-','+')              #priority: 2
	#and so on...
)

#token
class PCPL__ATH__token:
	def __init__(sbj, isOpe, textValue):
		sbj.isOpe     = isOpe
		sbj.textValue = textValue






# -------- COMPUTATIONS --------

#operand text check
def PCPL__ATH__checkOperand(zCtx, opa, allowFloat): #ret true if invalid

	#sub-directive => stop here, it must be decomposed first to allow 0 additional complexity level
	if '#' in opa:
		zCtx.dbg("Found a PCPL sub-directive => cancel arithmetic resolution.")
		return True

	#invalid 1st chr (negative sign)
	c = 0
	if opa[0] == '-':
		c = 1

	#invalid charset
	foundDot = not allowFloat #considering we already found a dot if we expect to read an integer (<=> don't allow any dot in integers)
	while c < len(opa):

		#only 1 dot allowed in number
		if opa[c] == '.':
			if foundDot:
				return True
			foundDot = True

		#must be a digit
		elif opa[c] not in string.digits:
			zCtx.dbg("Invalid character '" + opa[c] + "' at index " + str(c) + " in operand => cancel arithmetic resolution.")
			return True

		#increment
		c += 1

	#no problem found
	return False

#main entry point for computation
def PCPL__ATH__computeOperation(zCtx, ope, firstOpa, secondOpa, computeAsFloat):

	#check operands
	if PCPL__ATH__checkOperand(zCtx, firstOpa, computeAsFloat):
		return None
	if PCPL__ATH__checkOperand(zCtx, secondOpa, computeAsFloat):
		return None

	#floats
	if computeAsFloat:

		#read them
		firstOpaValue  = float(firstOpa) #<<<<<<<<<<<<<<<<<<<<<<<<<<< in Z, use dbl to store them
		secondOpaValue = float(secondOpa)

		#proceed to appropriate computation
		if ope == '-':
			return str(firstOpaValue - secondOpaValue)
		elif ope == '+':
			return str(firstOpaValue + secondOpaValue)
		elif ope == '*':
			return str(firstOpaValue * secondOpaValue)
		elif ope == '/':
			return str(firstOpaValue / secondOpaValue)
		elif ope == '&':
			return str(firstOpaValue & secondOpaValue)
		elif ope == '|':
			return str(firstOpaValue | secondOpaValue)
		elif ope == '^':
			return str(firstOpaValue ^ secondOpaValue)

	#integers
	else:

		#read them
		firstOpaValue  = str_dec_toS64(firstOpa)  #<<<<<<<<<<<<<<<<<<<<<<< in Z, use lng to store them
		secondOpaValue = str_dec_toS64(secondOpa)

		#proceed to appropriate computation <<<<<<<<<<<<<<<<<<<<<<<<< would have more sens in Z (other operators will be targetted)
		if ope == '-':
			return str(firstOpaValue - secondOpaValue)
		elif ope == '+':
			return str(firstOpaValue + secondOpaValue)
		elif ope == '*':
			return str(int(firstOpaValue * secondOpaValue))
		elif ope == '/':
			return str(int(firstOpaValue / secondOpaValue))
		elif ope == '&':
			return str(firstOpaValue & secondOpaValue)
		elif ope == '|':
			return str(firstOpaValue | secondOpaValue)
		elif ope == '^':
			return str(firstOpaValue ^ secondOpaValue)

	#no operator matching
	zCtx.internal("Unknown operand '" + ope + "' invoked in PCPL computation.")






# -------- TOOLS --------

#recurrent error case
def PCPL__ATH__inconsistencyError(zCtx, tooMuchLiteral):
	if tooMuchLiteral:
		zCtx.err("Inconsistency in precompiler arithmetic expression, got several consecutive operands without operator.")
	zCtx.err("Inconsistency in precompiler arithmetic expression, got several consecutive operators without operand.")

#check operator existence in expression
def PCPL__ATH__containsOperator(text):
	for c in text:
		if c in PCPL__ATH__OPERATORS:
			return True
	return False

#create token list from raw text expresion
def PCPL__ATH__tokenizeExpression(text):

	#tokenize literals & operators
	tokens  = []
	curText = ""
	for c in text:

		#found an operator
		if c in PCPL__ATH__OPERATORS:

			#did we have some text to store before => do it
			if len(curText) != 0:
				tokens.append( PCPL__ATH__token(False, curText) )
				curText = ""

			#then add that operator
			tokens.append( PCPL__ATH__token(True, c) )

		#blanks are to be ignored BUT THEY SERVE AS SEPARATOR BETWEEN TOKENS TOO !!!
		elif c in BLANKS:

			#did we have some text to store before => do it
			if len(curText) != 0:
				tokens.append( PCPL__ATH__token(False, curText) )
				curText = ""
			continue

		#not an operator => store into text
		else:
			curText += c

	#last text
	if len(curText) != 0:
		tokens.append( PCPL__ATH__token(False, curText) )

	#result
	return tokens



#negativity
def PCPL__ATH__mergeNegativeSignsAndCheckConsistency(zCtx, tokens):

	#STEP 1: first element
	if tokens[0].textValue == '-':
		if tokens[1].isOpe:
			PCPL__ATH__inconsistencyError(zCtx, False) #following another operator

		#apply negativity on the following one
		else:
			tokens[1].textValue = '-' + tokens[1].textValue
			tokens              = tokens[1:] #cut 1st element (negative sign)



	#STEP 2: other elements, look inside the rest of them 2 by 2
	concernedIdxs   = [] #fill a list of which literal requires a negative sign
	negSignToAttach = False
	for t in exactRange(1, len(tokens)-2):
		t1 = tokens[t  ]
		t2 = tokens[t+1]

		#ope as 2nd one
		if t2.isOpe:

			#2 consecutive operators
			if t1.isOpe:
				if t2.textValue == '-' and not negSignToAttach: #allowed if the next one is a negative sign => to be attached to next literal (must not be already waiting for attachment)
					negSignToAttach = True

				#else, inconsistency
				else:
					PCPL__ATH__inconsistencyError(zCtx, False)

		#literal as 2nd one
		else:

			#2 consecutive literals => inconsistency
			if not t1.isOpe:
				PCPL__ATH__inconsistencyError(zCtx, True)

			#was preceeded by a negative sign => OK to mark this idx
			if negSignToAttach:
				concernedIdxs.append(t+1)
				negSignToAttach = False

	#attach negative signs then
	for i in concernedIdxs:
		tokens[i].textValue = '-' + tokens[i].textValue

	#remove negative signs that has been set then
	concernedIdxs.reverse()
	for i in concernedIdxs: #!WARNING: ONLY WORKS BECAUSE concernedIdx IS FILLED WITH INCREASING VALUES !!!
		tokens.pop(i-1)



	#STEP 3: boudaries
	if tokens[0].isOpe:
		zCtx.err("Inconsistency in precompiler arithmetic expression, missing first operand to first operator.")
	if tokens[len(tokens)-1].isOpe:
		zCtx.err("Inconsistency in precompiler arithmetic expression, missing last operand to last operator.")






# -------- MAIN EXECUTION --------

#potentially got an arithmetic expression instead of a regular text => try to solve it first
def PCPL__ATH__solveArithmetic(zCtx, text):
	zCtx.deepDbg("Arithmetic expression detected.")
	tokens = PCPL__ATH__tokenizeExpression(text)

	#debug
	tokensText = ""
	for t in tokens:
		tokensText += "{ope:" + str(t.isOpe) + ",\"" + t.textValue + "\"},"
	zCtx.deepDbg("Arithmetic tokenization resulted into [" + tokensText + "].")

	#simpler case: lone token => not a real expression actually, can be treated directly
	if len(tokens) == 1:
		if tokens[0].isOpe: #lone operator => incomplete expression
			zCtx.err("Incomplete precompiler arithmetic expression given (lone operator found).")
		return tokens[0].textValue #lone literal => no need to go deeper



	#STEP 1: merge negative signs into their following literal if possible + check consistency btw
	PCPL__ATH__mergeNegativeSignsAndCheckConsistency(zCtx, tokens)

	#can result in having a lone token actually
	if len(tokens) == 1:
		return tokens[0].textValue



	#STEP 2: compute each operator by rank
	for rank in PCPL__ATH__OPERATOR_RANKS:

		#first, get the list of each concerned operator for this rank
		opeNbr     = int( (len(tokens)-1)/2 ) #nbr of operators among the given tokens
		tgtOpeIdxs = []
		for o in range(opeNbr):
			curOpeIdx = 2*o + 1
			if tokens[curOpeIdx].textValue in rank:
				tgtOpeIdxs.append(curOpeIdx)

		#then, for each of them, compute them with their nearest neighbor
		for i in range(len(tgtOpeIdxs)):
			opeIdx  = tgtOpeIdxs[i]
			opa1Idx = opeIdx-1
			opa2Idx = opeIdx+1

			#compute
			ope       = tokens[opeIdx].textValue[0]
			opa1      = tokens[opa1Idx].textValue
			opa2      = tokens[opa2Idx].textValue
			floatness = ('.' in opa1)
			res = PCPL__ATH__computeOperation(zCtx, ope, opa1, opa2, floatness)

			#invalid res from computation => invalid arithmetic expression
			if res is None:
				return None
			zCtx.deepDbg("Computation " + ope + " between " + opa1 + " and " + opa2 + " resulted into " + res + " with floatness[" + str(floatness) + "]")

			#store result at operator position
			tokens[opeIdx].textValue = res
			tokens.pop(opa2Idx) #operands have been computed, removing them
			tokens.pop(opa1Idx)

			#shift every other indexes to align we previous pops !WARNING: This works only because tgtOpeIdxs is filled with idxs in ascending order !!!
			lst_shift(tgtOpeIdxs, -2, start=i)

	#we should have only one token now
	if len(tokens) != 1:
		tokensText = ""
		for t in tokens:
			tokensText += "{ope:" + str(t.isOpe) + ",\"" + t.textValue + "\"},"
		zCtx.internal("Got more than 1 token at the end of PCPL arithmetic resolution " + tokensText)

	#res in last token
	zCtx.deepDbg("Arithmetic expression resulted into value \"" + tokens[0].textValue + "\" (ATH success).")
	return tokens[0].textValue

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

class PCPL__ATH__opeCall: #<=> POCall for PCPL (tiny bit simplified here)
	def __init__(sbj, opeText, firstOperand, secondOperand):
		sbj.opeText       = opeText
		sbj.firstOperand  = #lst[tokens]
		sbj.secondOperand = #lst[tokens]






# -------- SPECIFIC COMPUTATIONS --------

#...






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
	for i in concernedIdxs.reverse(): #!WARNING: ONLY WORKS BECAUSE concernedIdx IS FILLED WITH INCREASING VALUES !!!
		tokens.pop(i)



	#STEP 3: boudaries
	if tokens[0].isOpe:
		zCtx.err("Inconsistency in precompiler arithmetic expression, missing first operand to first operator.")
	if tokens[len(tokens)-1].isOpe:
		zCtx.err("Inconsistency in precompiler arithmetic expression, missing last operand to last operator.")






# -------- MAIN EXECUTION --------


def PCPL__ATH__tokensToOpeCall(tgtRank, tokens):

	#lone token
	if len(tokens) == 1:
		return 

	#
	opeNbr    = (len(tokens)-1)/2 #nbr of operators among the given tokens
	tgtTokens = []                #tokens of the targetted operators
	for o in range(opeNbr):
		curTk = tokens[o+1]
		if tokens[o+1] in tgtRank:
			tgtTokens.append(tokens[o+1])



#potentially got an arithmetic expression instead of a regular text => try to solve it first
def PCPL__ATH__solveArithmetic(zCtx, text):
	zCtx.deepDbg("Potential arithmetic expression detected.")
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



	#STEP 2: process each operator rank
	for rank in PCPL__ATH__OPERATOR_RANKS:
		res = PCPL__ATH__tokensToOpeCall(rank, tokens)

	

	#case 1: sub-directive (stop here, it must be decomposed first to allow 0 additional complexity level)
	elif c == '#':
		zCtx.dbg("Found a PCPL sub-directive => stop parsing current one")

	return text


#!/usr/bin/python3



# -------- IMPORTATIONS --------

#charsets
import string






# -------- TOOLS --------

#TO BE ADDED TO STDZ : this is a tiny bit more optimized version of ==(str,str).
#                      We don't compare lengths, assuming that they have been checked before.
#                      By the way, it must be called in ==(str,str) instead.
def str_cmp(s1, s2):
	for c in range(len(s1)):
		if s1[c] != s2[c]:
			return False
	return True

def str_subEqual( #that is tab_subequal in stdz actually
	t, second,
	length      = -1,
	first_from  = 0,
	second_from = 0
):
	if length == -1:
		length = len(t)

	#length constraint
	if (first_from >= len(t)) or (first_from+length > len(t)) or (second_from >= len(second)) or (second_from+length > len(second)):
		return False

	#check equality on specified range
	for c in range(length):
		if second[second_from + c] != t[first_from + c]:
			return False
	return True

def str_sub(s, start=None, stop=None):
	if start is None:
		start = 0
	if stop is None:
		stop = len(s)-1
	return s[start:stop+1]

def lst_sub(l, start=None, stop=None):
	return str_sub(l, start=start, stop=stop)

def str_isConvertible_int(s):
	if len(s) == 0:
		return False
	positiveS = s
	if s[0] == '-':
		positiveS = s[1:]
	for c in s:
		if c not in string.digits:
			return False
	return True



#strip
def str_getEndStripIndex(t, charset=" \t"):
	endIndex = len(t)-1
	for i in range(len(t)):
		if t[endIndex] not in charset:
			break
		endIndex -= 1
	return endIndex

def str_stripEnd(t, charset=" \t"):
	return str_sub(t, stop=str_getEndStripIndex(t, charset))

def str_getBeginningStripIndex(t, charset=" \t"):
	startIndex = 0
	for i in range(len(t)):
		if t[startIndex] not in charset:
			break
		startIndex += 1
	return startIndex

def str_stripBeginning(t, charset=" \t"):
	return str_sub(t, start=str_getBeginningStripIndex(t, charset))

def str_strip(t, charset=" \t"):
	return str_stripEnd(str_stripBeginning(t, charset), charset)

def str_expandTabs(s, expansionLength):
	result    = ""
	expansion = ' ' * expansionLength
	for c in s:
		if c == '\t':
			result += expansion
		else:
			result += c
	return result

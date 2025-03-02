#!/usr/bin/python3



# -------- TOOLS --------

#subequal
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

def str_stripEnd(t, charset=" \t"):
	len_t        = len(t)
	result       = ""
	currentIndex = len_t
	stripping    = True
	for i in range(len_t):
		currentIndex -= 1
		currentChr    = t[currentIndex]
		if stripping:
			if currentChr in charset:
				continue
			stripping = False
		result = currentChr + result
	return result

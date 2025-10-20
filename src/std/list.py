#!/usr/bin/python3



# -------- TOOLS --------

#stack-related behavior
def lst_isEmpty(l):
	return len(l) == 0

def lst_last(l):
	if lst_isEmpty(l):
		raise IndexError("Cannot get last element, list is empty.")
	return l[-1]

def lst_pop(l):
	last = lst_last(l)
	l.pop()
	return last

def lst_remove(l, idx):
	return l[:idx] + l[idx+1:]

def lst_copy(l): #only copying refs
	newL = []
	for e in l:
		newL.append(e)
	return newL

def lst_shift(l, shift, start=0):
	while start < len(l):
		l[start] += shift
		start += 1

def lst_insertBefore(l, idx, e):
	oldL = lst_copy(l)

	#clear lst
	for i in range(len(l)):
		l.pop()

	#fill it again, including additionnal element when asked
	for i in range(len(oldL)):
		if i == idx:
			l.append(e)
		l.append(oldL[i])

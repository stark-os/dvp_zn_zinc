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

def lst_remove(l, index):
	return l[:index] + l[index+1:]

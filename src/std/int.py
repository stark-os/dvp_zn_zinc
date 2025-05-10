#!/usr/bin/python3



# -------- TOOLS --------

#hexadecimal string representation on fixed amount of digits
def hexOnN(b, N):
	h = hex(b)[2:]
	if len(h) > N:
		print("ERROR IN STD/int.py")
		exit(1)
	while len(h) < N:
		h = '0' + h
	return h

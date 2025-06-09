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

def halfHex_toByt(h):
	if h == '0':
		return 0
	if h == '1':
		return 1
	if h == '2':
		return 2
	if h == '3':
		return 3
	if h == '4':
		return 4
	if h == '5':
		return 5
	if h == '6':
		return 6
	if h == '7':
		return 7
	if h == '8':
		return 8
	if h == '9':
		return 9
	if h == 'a':
		return 10
	if h == 'b':
		return 11
	if h == 'c':
		return 12
	if h == 'd':
		return 13
	if h == 'e':
		return 14
	if h == 'f':
		return 15

def hex_toByt(h1, h0):
	return (halfHex_toByt(h1) << 2) | halfHex_toByt(h0)

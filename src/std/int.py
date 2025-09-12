#!/usr/bin/python3



# -------- HEX --------

#hexadecimal string representation on fixed amount of digits
def hexOnN(b, N):

	#negativity with python
	if b < 1:
		if N == 2:
			return hexOnN(0xff + b, N)
		elif N == 4:
			return hexOnN(0xffff + b, N)
		elif N == 8:
			return hexOnN(0xffff_ffff + b, N)
		elif N == 16:
			return hexOnN(0xffff_ffff_ffff_ffff + b, )
		print("ERROR IN STD/int.py (invalid number of hex digits for negative output)")
		exit(1)

	#regular execution
	h = hex(b)[2:]
	if len(h) > N:
		print("ERROR IN STD/int.py")
		exit(1)
	while len(h) < N:
		h = '0' + h
	return h

#conversions
def chr_halfHex_toS1(h):
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
	return -1 #`ff
'''
MORE OPTIMIZED Z VERSION
s1 chr.halfHex_toS1(typ) {
	t = typ$s1
	if t >= '0'$s1 && t <= '9'$s1 { ret t - '0'$s1       }
	if t >= 'a'$s1 && t <= 'f'$s1 { ret t - 'a'$s1 + `0a }
	ret `ff
}
'''

def hex_toS1(h1, h0):
	return (chr_halfHex_toS1(h1) << 4) + chr_halfHex_toS1(h0)

def str_hex_toS1(s):
	if len(s) != 2:
		print("Hex string \"" + s + "\" must be only 2 characters to be converted into s1.")
		exit(1)
	pow1 = chr_halfHex_toS1(s[0])
	pow0 = chr_halfHex_toS1(s[1])
	if pow0 == -1 or pow1 == -1:
		print("Unconvertible hex string \"" + s + "\" into numerical value.")
		exit(1)
	return pow1 << 4 | pow0

def str_hex_toS2(s):
	if len(s) != 4:
		print("Hex string \"" + s + "\" must be only 4 characters to be converted into s2.")
		exit(1)
	pow3 = chr_halfHex_toS1(s[0])
	pow2 = chr_halfHex_toS1(s[1])
	pow1 = chr_halfHex_toS1(s[2])
	pow0 = chr_halfHex_toS1(s[3])
	if pow0 == -1 or pow1 == -1 \
	or pow2 == -1 or pow3 == -1:
		print("Unconvertible hex string \"" + s + "\" into numerical value.")
		exit(1)
	return \
		pow3 << 12 | pow2 << 8 | \
		pow1 <<  4 | pow0

def str_hex_toS4(s):
	if len(s) != 8:
		print("Hex string \"" + s + "\" must be only 8 characters to be converted into s4.")
		exit(1)
	pow7 = chr_halfHex_toS1(s[0])
	pow6 = chr_halfHex_toS1(s[1])
	pow5 = chr_halfHex_toS1(s[2])
	pow4 = chr_halfHex_toS1(s[3])
	pow3 = chr_halfHex_toS1(s[4])
	pow2 = chr_halfHex_toS1(s[5])
	pow1 = chr_halfHex_toS1(s[6])
	pow0 = chr_halfHex_toS1(s[7])
	if pow0 == -1 or pow1 == -1 \
	or pow2 == -1 or pow3 == -1 \
	or pow4 == -1 or pow5 == -1 \
	or pow6 == -1 or pow7 == -1:
		print("Unconvertible hex string \"" + s + "\" into numerical value.")
		exit(1)
	return \
		pow7 << 28 | pow6 << 24 | \
		pow5 << 20 | pow4 << 16 | \
		pow3 << 12 | pow2 <<  8 | \
		pow1 <<  4 | pow0

def str_hex_toS8(s):
	if len(s) != 16:
		print("Hex string \"" + s + "\" must be only 16 characters to be converted into s8.")
		exit(1)
	powF = chr_halfHex_toS1(s[ 0])
	powE = chr_halfHex_toS1(s[ 1])
	powD = chr_halfHex_toS1(s[ 2])
	powC = chr_halfHex_toS1(s[ 3])
	powB = chr_halfHex_toS1(s[ 4])
	powA = chr_halfHex_toS1(s[ 5])
	pow9 = chr_halfHex_toS1(s[ 6])
	pow8 = chr_halfHex_toS1(s[ 7])
	pow7 = chr_halfHex_toS1(s[ 8])
	pow6 = chr_halfHex_toS1(s[ 9])
	pow5 = chr_halfHex_toS1(s[10])
	pow4 = chr_halfHex_toS1(s[11])
	pow3 = chr_halfHex_toS1(s[12])
	pow2 = chr_halfHex_toS1(s[13])
	pow1 = chr_halfHex_toS1(s[14])
	pow0 = chr_halfHex_toS1(s[15])
	if pow0 == -1 or pow1 == -1 \
	or pow2 == -1 or pow3 == -1 \
	or pow4 == -1 or pow5 == -1 \
	or pow6 == -1 or pow7 == -1 \
	or pow8 == -1 or pow9 == -1 \
	or powA == -1 or powB == -1 \
	or powC == -1 or powD == -1 \
	or powE == -1 or powF == -1:
		print("Unconvertible hex string \"" + s + "\" into numerical value.")
		exit(1)
	return \
		powF << 60 | powE << 56 | \
		powD << 52 | powC << 48 | \
		powB << 44 | powA << 40 | \
		pow9 << 36 | pow8 << 32 | \
		pow7 << 28 | pow6 << 24 | \
		pow5 << 20 | pow4 << 16 | \
		pow3 << 12 | pow2 <<  8 | \
		pow1 <<  4 | pow0






# -------- DECIMAL --------

#conversions
def chr_dec_toS1(c):
	if c == '0':
		return 0
	if c == '1':
		return 1
	if c == '2':
		return 2
	if c == '3':
		return 3
	if c == '4':
		return 4
	if c == '5':
		return 5
	if c == '6':
		return 6
	if c == '7':
		return 7
	if c == '8':
		return 8
	if c == '9':
		return 9
	return -1 #`ff

#signed
MAX_LEN_DEC_S1 =  3 #(2** 7).toStr().length
MAX_LEN_DEC_S2 =  5 #(2**15).toStr().length
MAX_LEN_DEC_S4 = 10 #(2**31).toStr().length
MAX_LEN_DEC_S8 = 19 #(2**63).toStr().length

#unsigned
MAX_LEN_DEC_U1 =  3 #(2** 8).toStr().length
MAX_LEN_DEC_U2 =  5 #(2**16).toStr().length
MAX_LEN_DEC_U4 = 10 #(2**32).toStr().length
MAX_LEN_DEC_U8 = 20 #(2**64).toStr().length
def str_dec_toNum(s, sMaxLen, uMaxLen):
	if len(s) == 0:
		print("Empty string cannot be converted into numerical value.")
		exit(1)

	#negativity
	realLength    = len(s)
	negative      = (s[0] == '-')
	maxLenAllowed = uMaxLen
	if negative:
		realLength   -= 1
		maxLenAllowed = sMaxLen

	#too long
	if realLength > maxLenAllowed:
		print("Decimal string \"" + s + "\" too big to be converted into numerical value.")
		exit(1)

	#parsing by reading backward
	lastIdx = len(s)-1
	pow     = 1
	result  = 0
	for i in range(realLength):
		d       = chr_dec_toS1(s[lastIdx-i])
		if d == -1:
			print("Unconvertible decimal string \"" + s + "\" into numerical value.")
			exit(1)
		result += d * pow
		pow    *= 10

	#apply negativity if any
	if negative:
		result *= -1
	return result

def str_dec_toS1(s):
	return str_dec_toNum(s, MAX_LEN_DEC_S1, MAX_LEN_DEC_U1)

def str_dec_toS2(s):
	return str_dec_toNum(s, MAX_LEN_DEC_S2, MAX_LEN_DEC_U2)

def str_dec_toS4(s):
	return str_dec_toNum(s, MAX_LEN_DEC_S4, MAX_LEN_DEC_U4)

def str_dec_toS8(s):
	return str_dec_toNum(s, MAX_LEN_DEC_S8, MAX_LEN_DEC_U8)

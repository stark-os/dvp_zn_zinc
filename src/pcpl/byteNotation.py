#!/usr/bin/python3



# -------- IMPORTATIONS --------

#std
from std.character import *

#internal
from zctx import *






# -------- TOOLS --------

#prefix
BN_PREFIX = '`'

#escaped letters
BN_ALERT     = "07"
BN_BACKSPACE = "08"
BN_ESCAPE    = "1b"
BN_FORM_FEED = "0c"
BN_LINE_FEED = "0a"

#escaped symbols
BN_BACKSLASH    = "5c"
BN_SINGLE_QUOTE = "27"
BN_DOUBLE_QUOTE = "22"
BN_NULL         = "00"

BN_CARRIAGE_RETURN = "0d"
BN_HORIZONTAL_TAB  = "09"
BN_VERTICAL_TAB    = "0b"



#get byte notation (=> remove any text character from code => easier precompilation/compilation)
def BN_fromChr(zCtx, c, escaping=False):

	#special cases
	if escaping:

		#escaped letters
		if c == 'a':
			return BN_ALERT
		elif c == 'b':
			return BN_BACKSPACE
		elif c == 'e':
			return BN_ESCAPE
		elif c == 'f':
			return BN_FORM_FEED
		elif c == 'n':
			return BN_LINE_FEED
		elif c == 'r':
			return BN_CARRIAGE_RETURN
		elif c == 't':
			return BN_HORIZONTAL_TAB
		elif c == 'v':
			return BN_VERTICAL_TAB

		#escaped symbols
		elif c == '\\':
			return BN_BACKSLASH
		elif c == '\'':
			return BN_SINGLE_QUOTE
		elif c == '\"':
			return BN_DOUBLE_QUOTE
		elif c == '0':
			return BN_NULL

		#undefined escape sequence
		else:
			if chr_isPrintable(c):
				zCtx.error("Undefined escape sequence for character '" + c + "' (" + BN_PREFIX + chr_hex(c) + ").")
			else:
				zCtx.error("Undefined escape sequence for unprintable character : " + BN_PREFIX + chr_hex() + ".")

	#regular case
	else:
		return chr_hex(c)

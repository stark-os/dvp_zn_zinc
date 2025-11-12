#!/usr/bin/python3

import sys


#style
LOG__STYLE_RESET = "\x1b(B\x1b[m"
LOG__STYLE_BOLD  = "\x1b[1m"

#color
LOG__COLOR_NEUTRAL = "\x1b[38;5;245m" #gray
LOG__COLOR_INT     = "\x1b[38;5;190m" #yellow
LOG__COLOR_ERR     = "\x1b[38;5;196m" #red
LOG__COLOR_WRN     = "\x1b[38;5;21m"  #blue
LOG__COLOR_DBG     = "\x1b[38;5;48m"  #green
LOG__COLOR_DDBG    = "\x1b[38;5;46m"  #light green
LOG__COLOR_TEXT    = LOG__STYLE_RESET



#log
def log_int(txt):
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_INT + "[INT ERR] " + LOG__STYLE_RESET + LOG__COLOR_INT + l + '\n'
	sys.stderr.write(output[:-1] + LOG__STYLE_RESET)

def log_err(txt):
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_ERR + "[ ERROR ] " + LOG__STYLE_RESET + LOG__COLOR_ERR + l + '\n'
	sys.stderr.write(output[:-1] + LOG__STYLE_RESET)

def log_wrn(txt):
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_WRN + "[WARNING] " + LOG__STYLE_RESET + LOG__COLOR_WRN + l + '\n'
	sys.stderr.write(output[:-1] + LOG__STYLE_RESET)

def log_dbg(txt):
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_DBG + "[ DEBUG ] " + LOG__STYLE_RESET + LOG__COLOR_DBG + l + '\n'
	sys.stdout.write(output[:-1] + LOG__STYLE_RESET)

def log_deepDbg(txt):
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_DDBG + "[D-DEBUG] " + LOG__STYLE_RESET + LOG__COLOR_DDBG + l + '\n'
	sys.stdout.write(output[:-1] + LOG__STYLE_RESET)



#LF
def log_intLF(txt):
	log_int(txt)
	sys.stderr.write('\n')

def log_errLF(txt):
	log_err(txt)
	sys.stderr.write('\n')

def log_wrnLF(txt):
	log_wrn(txt)
	sys.stderr.write('\n')

def log_dbgLF(txt):
	log_dbg(txt)
	sys.stdout.write('\n')

def log_deepDbgLF(txt):
	log_deepDbg(txt)
	sys.stdout.write('\n')

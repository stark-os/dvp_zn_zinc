#!/usr/bin/python3

import sys


#style
LOG__STYLE_RESET = "\x1b(B\x1b[m"
LOG__STYLE_BOLD  = "\x1b[1m"

#color
LOG__COLOR_NEUTRAL = "\x1b[38;5;245m" #gray
LOG__COLOR_INT     = "\x1b[38;5;226m" #yellow
LOG__COLOR_ERR     = "\x1b[38;5;196m" #red
LOG__COLOR_WRN     = "\x1b[38;5;208m" #orange
LOG__COLOR_DBG0    = "\x1b[38;5;46m"  #green
LOG__COLOR_DBG1    = "\x1b[38;5;48m"  #light green
LOG__COLOR_DBG2    = "\x1b[38;5;115m" #light cyan
LOG__COLOR_TEXT    = LOG__STYLE_RESET

#lvl
LOG__LVL_ERR  = 0
LOG__LVL_WRN  = 1
LOG__LVL_INF  = 2
LOG__LVL_DBG0 = 3
LOG__LVL_DBG1 = 4
LOG__LVL_DBG2 = 5
log_lvl = [LOG__LVL_INF] #using a lst to have a REAL GBL VAR (pythonic limitation...)



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
	if log_lvl[0] < LOG__LVL_WRN:
		return
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_WRN + "[WARNING] " + LOG__STYLE_RESET + LOG__COLOR_WRN + l + '\n'
	sys.stderr.write(output[:-1] + LOG__STYLE_RESET)

def log_dbg0(txt):
	if log_lvl[0] < LOG__LVL_DBG0:
		return
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_DBG0 + "[DEBUG 0] " + LOG__STYLE_RESET + LOG__COLOR_DBG0 + l + '\n'
	sys.stdout.write(output[:-1] + LOG__STYLE_RESET)

def log_dbg1(txt):
	if log_lvl[0] < LOG__LVL_DBG1:
		return
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_DBG1 + "[DEBUG 1] " + LOG__STYLE_RESET + LOG__COLOR_DBG1 + l + '\n'
	sys.stdout.write(output[:-1] + LOG__STYLE_RESET)

def log_dbg2(txt):
	if log_lvl[0] < LOG__LVL_DBG2:
		return
	output = ""
	for l in txt.split('\n'):
		output += LOG__STYLE_BOLD + LOG__COLOR_DBG2 + "[DEBUG 2] " + LOG__STYLE_RESET + LOG__COLOR_DBG2 + l + '\n'
	sys.stdout.write(output[:-1] + LOG__STYLE_RESET)



#LF
def log_intLF(txt):
	log_int(txt)
	sys.stderr.write('\n')

def log_errLF(txt):
	log_err(txt)
	sys.stderr.write('\n')

def log_wrnLF(txt):
	if log_lvl[0] < LOG__LVL_WRN:
		return
	log_wrn(txt)
	sys.stderr.write('\n')

def log_dbg0LF(txt):
	if log_lvl[0] < LOG__LVL_DBG0:
		return
	log_dbg0(txt)
	sys.stdout.write('\n')

def log_dbg1LF(txt):
	if log_lvl[0] < LOG__LVL_DBG1:
		return
	log_dbg1(txt)
	sys.stdout.write('\n')

def log_dbg2LF(txt):
	if log_lvl[0] < LOG__LVL_DBG2:
		return
	log_dbg2(txt)
	sys.stdout.write('\n')

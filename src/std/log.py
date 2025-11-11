#!/usr/bin/python3

import sys


def log_int(txt):
	output = ""
	for l in txt.split('\n'):
		output += "[INT ERR] " + l + '\n'
	sys.stderr.write(output)

def log_err(txt):
	output = ""
	for l in txt.split('\n'):
		output += "[ ERROR ] " + l + '\n'
	sys.stderr.write(output)

def log_wrn(txt):
	output = ""
	for l in txt.split('\n'):
		output += "[WARNING] " + l + '\n'
	sys.stderr.write(output)

def log_dbg(txt):
	output = ""
	for l in txt.split('\n'):
		output += "[ DEBUG ] " + l + '\n'
	sys.stdout.write(output)

def log_deepDbg(txt):
	output = ""
	for l in txt.split('\n'):
		output += "[D-DEBUG] " + l + '\n'
	sys.stdout.write(output)



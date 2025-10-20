#!/usr/bin/python3



# -------- TOOLS --------

#exact range
def exactRange(start, stop, step=0):
	if stop >= start:
		if step == 0:
			step = 1
		return range(start, stop+1, step)
	if step == 0:
		step = -1
	return range(start-1, stop-1, step)

#!/usr/bin/python3



# -------- TYPE DEF --------

#stack object
class Stack:
	def __init__(self):
		self.data = []

	def push(self, element):
		self.data.append(element)

	def isEmpty(self):
		return len(self.data) == 0

	def pop(self):
		if len(self.data) == 0:
			raise IndexError("Stack is empty")
		last = self.data[-1]
		self.data = self.data[:-1]
		return last

	def isIn(self, element):
		return element in self.data

#!/usr/bin/python3



# -------- TYPE DEF --------

#stack object (completely optionnal type, we can consider these functions to be applied on lst directly)
class Stack:
	def __init__(self):
		self.data = []

	def push(self, element):
		self.data.append(element)

	def isEmpty(self):
		return len(self.data) == 0

	def last(self):
		if self.isEmpty():
			raise IndexError("Cannot get last element, stack is empty.")
		return self.data[-1]

	def pop(self):
		last      = self.last()
		self.data = self.data[:-1]
		return last

	def isIn(self, element):
		return element in self.data

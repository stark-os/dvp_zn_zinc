
#!/usr/bin/python3



# .-------------- Config Python Library [0.1.0] -------------.
# |                                                          |
# |     This library is the official parser tool for Config  |
# | files. It includes 4 functions :                         |
# |   - config.fromText() #get data from raw text            |
# |   - config.toText()   #get raw text from data            |
# |   - config.read()     #get data from file                |
# |   - config.write()    #write data into file              |
# |                                                          |
# |     For more information about this syntax, please check |
# | out the main repository for documentation:               |
# |                                                          |
# |           https://github.com/iasebsil83/config           |
# |                                                          |
# | Let's Code !                                     By I.A. |
# |                                                          |
# |*********************************************************************|
# |  LICENSE :                                                          |
# |                                                                     |
# |  Config_Python3                                                     |
# |  Copyright (C) 2023 Sebastien SILVANO                               |
# |                                                                     |
# |  This library is free software; you can redistribute it and/or      |
# |  modify it under the terms of the GNU Lesser General Public         |
# |  License as published by the Free Software Foundation; either       |
# |  version 2.1 of the License, or (at your option) any later version. |
# |                                                                     |
# |  This library is distributed in the hope that it will be useful,    |
# |  but WITHOUT ANY WARRANTY; without even the implied warranty of     |
# |  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU  |
# |  Lesser General Public License for more details.                    |
# |                                                                     |
# |  You should have received a copy of the GNU Lesser General Public   |
# |  License along with this library.                                   |
# |                                                                     |
# |  If not, see <https://www.gnu.org/licenses/>.                       |
# '---------------------------------------------------------------------'






# ---- CONSTANTS ----

#special characters (default values)
COMMENT_CHARACTER    = '#'
LINE_END_CHARACTER   = '\n'
SEPARATION_CHARACTER = '\t'

#options (default values)
ADDITIONAL_SPACES_ALLOWED = True #disable it if you want to store blanks for instance






# ---- DATA <-> TEXT ----

def fromText(
	text,

	#characters
	comment_character        = COMMENT_CHARACTER,
	lineEnd_character        = LINE_END_CHARACTER,
	separation_character     = SEPARATION_CHARACTER,

	#options
	additionnalSpacesAllowed = ADDITIONAL_SPACES_ALLOWED
):
	'''
	Convert a Config text into dictionnary.

	text: str

	Returns The dictionnary corresponding to the given configuration file.
	'''

	#prepare final result
	result = {}

	#parsing states
	IN_NAME       = 0
	IN_SEPARATION = 1
	IN_VALUE      = 2

	#current state
	current_state = IN_NAME
	current_name  = ""
	current_value = ""

	#split text by lines
	lines = text.split(lineEnd_character)

	#for each line
	for l,line in enumerate(lines):

		#reset fields (current_value is reset in separation field analysis)
		current_state = IN_NAME
		current_name  = ""

		#for each character in line
		line_len = len(line)
		for c in range(line_len):

			#option : allow additional spacing
			if additionnalSpacesAllowed:
				if line[c] == ' ':
					continue

			#arriving on a comment => stopping line parsing
			if line[c] == comment_character:
				break

			#case 2.1: reading name
			if current_state == IN_NAME:

				#separation found
				if line[c] == separation_character:

					#check name length before going further
					if len(current_name) == 0:
						raise ValueError("Missing name (line " + str(l+1) + ").")

					#turn into separation mode
					current_state = IN_SEPARATION
					continue

				#regular character => add it to current name
				current_name += line[c]

			#case 2.2: reading separation field
			elif current_state == IN_SEPARATION:

				#regular character => reading value now
				if line[c] != separation_character:
					current_state = IN_VALUE

					#option : allow spacing before comments
					if not additionnalSpacesAllowed or current_value != ' ':
						current_value = line[c]
					continue

			#case 2.3: reading value
			else:

				#separation character found => ERROR (several separations are not allowed)
				if line[c] == separation_character:
					raise ValueError("Could not parse Config text, several separation fields detected (line " + str(l+1) + ").")

				#regular text => add it to the current value
				current_value += line[c]

		#check name
		current_name_len = len(current_name)
		if current_state == IN_NAME:

			#empty line (or comment only)
			if current_name_len == 0:
				continue

			#only name defined
			else:
				raise ValueError("Missing separation character after name (line " + str(l+1) + ").")

		#check other fields
		else:
			if current_name_len == 0:
				raise ValueError("Could not parse Config text, missing name field (line " + str(l+1) + ").")
			if len(current_value) == 0:
				raise ValueError("Could not parse Config text, missing value field (line " + str(l+1) + ").")

		#correct configuration structure
		result[current_name] = current_value

	return result



#data -> to text
def toText(
	data,

	#characters
	lineEnd_character    = LINE_END_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
):
	'''
	Convert a dictionnary into Config text.

	data: dict

	Returns a Config text corresponding to the given data.
	'''

	#check structure type
	if not isinstance(data, dict):
		raise ValueError("Could not unparse Config text, data has incorrect type (only dict allowed).")

	#check data complexity
	for d in data.keys():
		if not isinstance(data[d], str):
			raise ValueError("Could not unparse Config text, name '" + d + "' has incorrect type (only str allowed).")

	#parse data
	result = ""
	for d in data.keys():
		result += d + separation_character + data[d] + lineEnd_character

	return result






# ---- READ / WRITE ----

#read text from file => return data as dict
def read(
	filename,

	#characters
	comment_character        = COMMENT_CHARACTER,
	lineEnd_character        = LINE_END_CHARACTER,
	separation_character     = SEPARATION_CHARACTER,

	#options
	additionnalSpacesAllowed = ADDITIONAL_SPACES_ALLOWED
):
	'''
	Read a Config file.

	filename: str

	Returns a dictionnary representing the configuration read from the file.
	'''

	#read text from file
	f = open(filename, "r")
	text = f.read()
	f.close()

	#parse
	return fromText(
		text,

		#characters
		comment_character        = comment_character,
		lineEnd_character        = lineEnd_character,
		separation_character     = separation_character,

		#options
		additionnalSpacesAllowed = additionnalSpacesAllowed
	)




#write data into file
def write(
	filename, data,

	#characters
	comment_character        = COMMENT_CHARACTER,
	lineEnd_character        = LINE_END_CHARACTER,
	separation_character     = SEPARATION_CHARACTER,

	#options
	additionnalSpacesAllowed = ADDITIONAL_SPACES_ALLOWED
):
	'''
	Write data into a Config file.

	filename: str
	data: dict

	Write the data respecting the Config syntax.
	'''

	#unparse
	text = toText(
		data,

		#characters
		lineEnd_character        = lineEnd_character,
		separation_character     = separation_character,
	)

	#write out
	f = open(filename, "w")
	f.write(text)
	f.close()

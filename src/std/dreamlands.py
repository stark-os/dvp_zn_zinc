#!/usr/bin/python3



# .-------------- DREAMLANDS Python Library [0.1.0] -------------.
# |                                                              |
# |     This library is the official parser tool for DREAMLANDS  |
# | files. It includes 4 functions :                             |
# |   - dreamlands.fromText() #get data from raw text            |
# |   - dreamlands.toText()   #get raw text from data            |
# |   - dreamlands.read()     #get data from file                |
# |   - dreamlands.write()    #write data into file              |
# |                                                              |
# |     For more information about this syntax, please check     |
# | out the main repository for documentation:                   |
# |                                                              |
# |           https://github.com/iasebsil83/DREAMLANDS           |
# |                                                              |
# | Let's Code !                                         By I.A. |
# |                                                              |
# |*********************************************************************|
# |  LICENSE :                                                          |
# |                                                                     |
# |  DREAMLANDS_Python3                                                 |
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






# ---- IMPORTATIONS ----

#charsets
import string






# ---- OPTIONS ----

#allow additional spaces
ADDITIONAL_SPACES_ALLOWED = True

#debug mode
DEBUG_MODE = False

#allow external files importation (if False, importations will be skipped)
EXTERNAL_IMPORTATIONS_ALLOWED = True

#python character optimization (if True, python strings of 1 character long will be interpreted as characters)
PYTHON_CHARACTERS_OPTIMIZATION = True # This is only applicable in function toText()






# ---- CONSTANTS ----

#blanks : DO NOT MODIFY
BLANKS = (' ', '\t')






# ---- CONSTANTS ----

#special characters (defaults)
COMMENT_CHARACTER    = '#'
LINE_END_CHARACTER   = '\n'
NEW_FILE_CHARACTER   = '>'
SEPARATION_CHARACTER = ':'
TABULATION_CHARACTER = '\t'

#keys
KEYS_CHARACTERS_ALLOWED = string.ascii_letters + '_' + string.digits

#escaped characters (text elements)
ESCAPED_CHARACTERS_MAP = {
	'a' :'\a',
	'b' :'\b',
	'e' :'\x1b', # '\e' is not interpreted in python3
	'f' :'\f',
	'n' :'\n',
	'r' :'\r',
	't' :'\t',
	'v' :'\v',
	'\\':'\\',
	'\'':'\'',
	'\"':'\"'
}

#some internal constants (must be accessible by several functions)
I__LINE_NBR  = 0
I__COLM_NBR  = 1
I__DEPTH     = 2
I__KEY       = 3
I__VALUE     = 4






# ---- GLOBAL DECLARATIONS ----

#current index of instructs during unparsing
class _:
	instructsIndex = 0






# ---- DATA <-> TEXT ----

#error shortcut
def __checkChrLen(line_nbr, colm_nbr, current_buffer):
	'''
	[INTERNAL FUNCTION] Check if a character can be added to the current state.

	line_nbr:       int
	colm_nbr:       int
	current_buffer: str

	Returns void.
	'''
	if len(current_buffer) != 0:
		raise ValueError(
			"Only one character is allowed in character declaration (line " + \
			str(line_nbr) + " column "                                      + \
			str(colm_nbr) + ")."
		)

def __invalidEscChr(line_nbr, colm_nbr, char):
	'''
	[INTERNAL FUNCTION] .

	linr_nbr: int
	colm_nbr: int

	Returns void.
	'''
	raise ValueError(
		"Invalid escaped character found with value " + str(int(char)) + ". (line " + \
		str(line_nbr) + " column " + \
		str(colm_nbr) + ")."
	)



#data <- from text
def fromText(
	text,

	#characters
	comment_character    = COMMENT_CHARACTER,
	lineEnd_character    = LINE_END_CHARACTER,
	newFile_character    = NEW_FILE_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
	tabulation_character = TABULATION_CHARACTER,

	#options
	additionnalSpacesAllowed     = ADDITIONAL_SPACES_ALLOWED,
	debugMode                    = DEBUG_MODE,
	externalImportationsAllowed  = EXTERNAL_IMPORTATIONS_ALLOWED,
	pythonCharactersOptimization = PYTHON_CHARACTERS_OPTIMIZATION
):
	'''
	Convert a DREAMLANDS text into data structure.

	text: str

	Returns a data structure corresponding to the given DREAMLANDS text (dict/list).
	'''

	#get instruction list of current text
	instructs = __textToInstructs(
		text,

		#characters
		comment_character    = comment_character,
		lineEnd_character    = lineEnd_character,
		newFile_character    = newFile_character,
		separation_character = separation_character,
		tabulation_character = tabulation_character,

		#options
		additionnalSpacesAllowed     = additionnalSpacesAllowed,
		debugMode                    = debugMode,
		externalImportationsAllowed  = externalImportationsAllowed,
		pythonCharactersOptimization = pythonCharactersOptimization
	)

	#complete instruction set with external importations
	i = 0
	len_instructs = len(instructs)
	importedFiles = []
	while i < len_instructs:
		if debugMode:
			print("[DEBUG] Completing instructs : [" + str(i) + "] = " + str(instructs[i]) + " len " + str(len_instructs))

		#importation detected => add it to current instructs
		if instructs[i][I__DEPTH] < 0:

			#anti-recursivity check
			if instructs[i][I__VALUE] in importedFiles:
				raise RecursionError("Recursive importation detected : file '" + instructs[i][I__VALUE] + "' already imported once.")
			importedFiles.append(instructs[i][I__VALUE])

			#read external file
			f = open(instructs[i][I__VALUE], "r")
			extText = f.read()
			f.close()

			#get its instructions
			extIns = __textToInstructs(
				extText,

				#characters
				comment_character    = comment_character,
				lineEnd_character    = lineEnd_character,
				newFile_character    = newFile_character,
				separation_character = separation_character,
				tabulation_character = tabulation_character,

				#options
				additionnalSpacesAllowed     = additionnalSpacesAllowed,
				debugMode                    = debugMode,
				externalImportationsAllowed  = externalImportationsAllowed,
				pythonCharactersOptimization = pythonCharactersOptimization
			)
			len_extIns = len(extIns)

			#for each imported instruction
			for ei in range(len_extIns):
				instructs.insert(i+ei, extIns[ei])
			instructs.pop(i+len_extIns)

			#re-calculate global length
			len_instructs = len(instructs)

		#increment (only on non-import instruction)
		else:
			i += 1

	#no data
	if len(instructs) == 0:
		return None

	#check first element
	if instructs[0][I__DEPTH] != 0:
		raise IndentationError("Incorrect indent for first element : zero-depth is required.")

	#check last element parentality
	if instructs[-1][I__VALUE] is None:
		raise ValueError("Incorrect value for last element : child element required.")

	#debug
	if debugMode:
		print("[DEBUG] Completed instructs = [")
		for i in instructs:
			print("\t" + str(i) + ",")
		print("]")

	#finally translate instructions into data
	_.instructsIndex = 0
	return __instructsToData(
		instructs,

		#characters
		comment_character    = comment_character,
		lineEnd_character    = lineEnd_character,
		newFile_character    = newFile_character,
		separation_character = separation_character,
		tabulation_character = tabulation_character,

		#options
		additionnalSpacesAllowed     = additionnalSpacesAllowed,
		debugMode                    = debugMode,
		externalImportationsAllowed  = externalImportationsAllowed,
		pythonCharactersOptimization = pythonCharactersOptimization
	)



#parsing
def __textToInstructs(
	text,

	#characters
	comment_character    = COMMENT_CHARACTER,
	lineEnd_character    = LINE_END_CHARACTER,
	newFile_character    = NEW_FILE_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
	tabulation_character = TABULATION_CHARACTER,

	#options
	additionnalSpacesAllowed     = ADDITIONAL_SPACES_ALLOWED,
	debugMode                    = DEBUG_MODE,
	externalImportationsAllowed  = EXTERNAL_IMPORTATIONS_ALLOWED,
	pythonCharactersOptimization = PYTHON_CHARACTERS_OPTIMIZATION
):
	'''
	[INTERNAL FUNCTION] Parse raw text to an instruction list

	text: str

	Returns the list of instructions extracted from the text.
	'''

	# STEP 1 : SEPARATE INSTRUCTIONS

	#some temporary constants (indexes inside raw_instructs list)
	RI__LINE_NBR = 0
	RI__COLM_NBR = 1
	RI__RAW_TEXT = 2
	RI__CHR_TEXT = 3
	RI__STR_TEXT = 4

	#field detection
	inComment = False
	inChr     = False
	inStr     = False
	escaping  = False

	#just separate instructions
	raw_instructs = [
		[1, 1, "", "", ""]
	]
	line_nbr = 1
	colm_nbr = 0
	for c, char in enumerate(text):
		colm_nbr += 1
		if char == '\n':
			line_nbr += 1
			colm_nbr  = 1
			inComment = False

		#get latest raw_instruct location for error messages (optimization shortcut)
		latestRI_lineNbr = raw_instructs[-1][RI__LINE_NBR]
		latestRI_colmNbr = raw_instructs[-1][RI__COLM_NBR]



		#case 1 : IN CHARACTER
		if inChr:

			#escaped sequences
			if escaping:
				__checkChrLen(
					latestRI_lineNbr,
					latestRI_colmNbr,
					raw_instructs[-1][RI__CHR_TEXT]
				)
				escaping = False
				try:
					raw_instructs[-1][RI__CHR_TEXT] += ESCAPED_CHARACTERS_MAP[char]
				except KeyError:
					__invalidEscChr(latestRI_lineNbr, latestRI_colmNbr, char)

			#not escaping (reading normaly)
			else:

				#start escaping
				if char == '\\':
					escaping = True

				#end of text field detection
				elif char == '\'':
					inChr = False

				#regular character => add it
				else:
					__checkChrLen(
						latestRI_lineNbr,
						latestRI_colmNbr,
						raw_instructs[-1][RI__CHR_TEXT]
					)
					raw_instructs[-1][RI__CHR_TEXT] += char



		#case 2 : IN STRING
		elif inStr:

			#escaped sequences
			if escaping:
				escaping = False
				try:
					raw_instructs[-1][RI__STR_TEXT] += ESCAPED_CHARACTERS_MAP[char]
				except KeyError:
					__invalidEscChr(latestRI_lineNbr, latestRI_colmNbr, char)

			#not escaping (reading normally)
			else:

				#start escaping
				if char == '\\':
					escaping = True

				#end of text field detection
				elif char == '\"':
					inStr = False

				#regular character => add it
				else:
					raw_instructs[-1][RI__STR_TEXT] += char



		#case 3 : RAW TEXT
		elif not inComment:

			#field detection : comment
			if char == comment_character:
				inComment = True

			#field detection : character
			elif char == '\'':
				inChr = True

				#empty character (double character delimiter)
				if len(text) > c+1 and text[c+1] == '\'':
					raise ValueError(
						"Empty characters are not supported (line " + \
						str(latestRI_lineNbr) + " column "          + \
						str(latestRI_colmNbr) + ")."
					)

			#field detection : string
			elif char == '\"':
				inStr = True

				#empty string (double string delimiter)
				if len(text) > c+1 and text[c+1] == '\"':
					raise ValueError(
						"Empty strings are not supported (line " + \
						str(latestRI_lineNbr) + " column "       + \
						str(latestRI_colmNbr) + ")."
					)

			#end of instruction => passing to the new one
			elif char == lineEnd_character:
				raw_instructs.append(
					[line_nbr, colm_nbr, "", "", ""]
				)

			#add raw text to current instruction
			else:
				raw_instructs[-1][RI__RAW_TEXT] += char

	#missing text field delimiter
	if inChr:
		raise ValueError(
			"Missing character delimiter at end of declaration (line " + \
			str(raw_instructs[-1][RI__LINE_NBR]) + " column "          + \
			str(raw_instructs[-1][RI__COLM_NBR]) + ")."
		)
	if inStr:
		raise ValueError(
			"Missing string delimiter at end of declaration (line " + \
			str(raw_instructs[-1][RI__LINE_NBR]) + " column "       + \
			str(raw_instructs[-1][RI__COLM_NBR]) + ")."
		)

	#remove additional spaces (optional)
	if additionnalSpacesAllowed:
		for a in range(len(raw_instructs)):

			#remove spaces in raw_instructs[a][RI__RAW_TEXT]
			ri_rawText = ""
			for c in raw_instructs[a][RI__RAW_TEXT]:
				if c != ' ':
					ri_rawText += c
			raw_instructs[a][RI__RAW_TEXT] = ri_rawText

	#debug
	if debugMode:
		print("[DEBUG] raw_instructs = [")
		for ri in raw_instructs:
			print("\t" + str(ri) + ",")
		print("]")



	# STEP 2 : SEPARATE FIELDS (inside each raw instruction)

	#instructions in strict format
	instructs = []

	#for each instruction
	for ri in raw_instructs:
		len_ri_raw_text = len(ri[RI__RAW_TEXT])
		len_ri_chr_text = len(ri[RI__CHR_TEXT])
		len_ri_str_text = len(ri[RI__STR_TEXT])



		#phase 1 : PREPARATION & OBVIOUS CASES

		#empty instruction => skip it
		if len_ri_raw_text == 0 and len_ri_chr_text == 0 and len_ri_str_text == 0:
			continue

		#both character & string declaration => NOT ALLOWED
		if len_ri_chr_text != 0 and len_ri_str_text != 0:
			raise ValueError(
				"Could not have both character and string declaration in only one instruction (line " + \
				str(ri[RI__LINE_NBR]) + " column "                                                    + \
				str(ri[RI__COLM_NBR]) + ")."
			)



		#phase 2 : IMPORTATIONS

		#importation detected
		if ri[RI__RAW_TEXT].startswith(newFile_character):

			#add it if option enabled
			if externalImportationsAllowed:
				instructs.append([
					ri[RI__LINE_NBR],    #line_nbr
					ri[RI__COLM_NBR],    #colm_nbr
					-1,                  #depth : negative means IMPORTATION FLAG
					"",                  #key
					ri[RI__RAW_TEXT][1:] #value : here, filename is stored
				])

			#else : ignore this instruction
			continue

		#not an importation => create a new empty instruction
		else:
			instructs.append([
				ri[RI__LINE_NBR], #line_nbr
				ri[RI__COLM_NBR], #colm_nbr
				0,                #depth
				"",               #key
				None              #value (None also means : PARENT)
			])



		#phase 3 : ANALYSIS

		#set depth
		for c in ri[RI__RAW_TEXT]:
			if c == tabulation_character:
				instructs[-1][I__DEPTH] += 1
				ri[RI__RAW_TEXT] = ri[RI__RAW_TEXT][1:] #cut the 1st character
			else:
				break

		#separate key-value pair
		pair = ri[RI__RAW_TEXT].split(separation_character)
		if len(pair) != 2:
			raise ValueError(
				"One separation character is required per instruction (line " + \
				str(ri[RI__LINE_NBR]) + " column "                            + \
				str(ri[RI__COLM_NBR]) + ")."
			)
		instructs[-1][I__KEY] = pair[0]
		value                 = pair[1]

		#check key name length
		if len(instructs[-1][I__KEY]) == 0:
			raise ValueError(
				"Missing key name : at least one character is required (line " + \
				str(ri[RI__LINE_NBR]) + " column "                             + \
				str(ri[RI__COLM_NBR]) + ")."
			)

		#check key name
		if instructs[-1][I__KEY] != '-':
			for c in instructs[-1][I__KEY]:
				if c not in KEYS_CHARACTERS_ALLOWED:
					raise ValueError(
						"Invalid character in key name : use only [a-z], [A-Z], [0-9] & underscores (line " + \
						str(ri[RI__LINE_NBR]) + " column "                                                  + \
						str(ri[RI__COLM_NBR]) + ")."
					)



		#case 1 : characters, strings or parent
		if len(value) == 0:

			#case 1.1 : character declaration
			if len_ri_chr_text != 0:          #can only be 0 or 1
				instructs[-1][I__VALUE] = ri[RI__CHR_TEXT][0]

			#case 1.2 : string declaration
			elif len_ri_str_text != 0:
				instructs[-1][I__VALUE] = ri[RI__STR_TEXT]

			#analysis terminated
			continue



		#case 2 : booleans
		if value == "false":
			instructs[-1][I__VALUE] = False
			continue
		if value == "true":
			instructs[-1][I__VALUE] = True
			continue



		#case 3 : numbers

		#negative values
		negative = False
		if value[0] == '-':
			negative = True
			value = value[1:] #cut negative sign (performance optimization)

		#check every character of value
		dotFound = False
		for v in value:
			if v == '.':

				#dot already found => only one coma is allowed
				if dotFound:
					raise ValueError(
						"Multiple dots found in floating point value for key '" + instructs[-1][I__KEY] + "' (line " + \
						str(ri[RI__LINE_NBR]) + " column "                                                           + \
						str(ri[RI__COLM_NBR]) + ")."
					)

				#1st dot found
				dotFound = True
				continue

			#non-digit character => undefined value
			if v not in string.digits:
				raise ValueError(
					"Undefined value for key '" + instructs[-1][I__KEY] + "' (line " + \
					str(ri[RI__LINE_NBR]) + " column "                               + \
					str(ri[RI__COLM_NBR]) + ")."
				)

		#floating point number
		if dotFound:
			instructs[-1][I__VALUE] = float(value)

		#integer
		else:
			instructs[-1][I__VALUE] = int(value)

		#apply negativity afterwards
		if negative:
			instructs[-1][I__VALUE] = -( instructs[-1][I__VALUE] )

	#debug
	if debugMode:
		print("[DEBUG] instructs = [")
		for i in instructs:
			print("\t" + str(i) + ",")
		print("]")

	return instructs



#translate intructions into data
def __getFullValue(instructs, current_depth):
	'''
	[INTERNAL FUNCTION] Get value of instruction even if it is a parent.
	This function is 2-times recursive with __instructsToData().

	instructs: list

	Returns data structure (list, dictionnary, or raw element).
	'''

	#get brother value : if parent, first process its children
	value = instructs[_.instructsIndex][I__VALUE]
	_.instructsIndex += 1
	if value is None:
		value = __instructsToData(
			instructs, current_depth+1,

			#characters
			comment_character    = comment_character,
			lineEnd_character    = lineEnd_character,
			newFile_character    = newFile_character,
			separation_character = separation_character,
			tabulation_character = tabulation_character,

			#options
			additionnalSpacesAllowed     = additionnalSpacesAllowed,
			debugMode                    = debugMode,
			externalImportationsAllowed  = externalImportationsAllowed,
			pythonCharactersOptimization = pythonCharactersOptimization
		)

	return value

def __instructsToData(
	instructs,
	current_depth=0,

	#characters
	comment_character    = COMMENT_CHARACTER,
	lineEnd_character    = LINE_END_CHARACTER,
	newFile_character    = NEW_FILE_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
	tabulation_character = TABULATION_CHARACTER,

	#options
	additionnalSpacesAllowed     = ADDITIONAL_SPACES_ALLOWED,
	debugMode                    = DEBUG_MODE,
	externalImportationsAllowed  = EXTERNAL_IMPORTATIONS_ALLOWED,
	pythonCharactersOptimization = PYTHON_CHARACTERS_OPTIMIZATION
):
	'''
	[INTERNAL FUNCTION] Translates an instruction list into data structure.
	This function is 2-times recursive with __getFullValue().

	instructs: list

	Returns data structure (list or dictionnary).
	'''

	#1st instruction is a list element => global data will be a list
	data_isList = (instructs[_.instructsIndex][I__KEY] == '-')
	if data_isList:
		data = []
	else:
		data = {} #else, a dictionnary

	#for each instruction (mind that instructsIndex is NOT incremented in general scope of loop but in statements)
	instructs_len = len(instructs)
	while _.instructsIndex < instructs_len:

		#debug
		if debugMode:
			print("[DEBUG] translating into data " + str(instructs[_.instructsIndex]) + "  instructsIndex " + str(_.instructsIndex) + ".")

		#case 1 : too much indent
		if instructs[_.instructsIndex][I__DEPTH] > current_depth+1:
			raise IndentationError(
				"Too much indent for instruct '" + instructs[_.instructsIndex][I__KEY] + "' (line " + \
				str(instructs[_.instructsIndex][I__LINE_NBR]) + " column "                          + \
				str(instructs[_.instructsIndex][I__COLM_NBR]) + ")."
			)

		#case 2 : child element
		elif instructs[_.instructsIndex][I__DEPTH] == current_depth+1:

			#children are processed by their parents (considerated as brothers between them)
			raise ValueError(
				"Children element '" + instructs[_.instructsIndex][I__KEY] + "' detected but no parent declared (line " + \
				str(instructs[_.instructsIndex][I__LINE_NBR]) + " column "                                              + \
				str(instructs[_.instructsIndex][I__COLM_NBR]) + ")."
			)

		#case 3 : brother element
		elif instructs[_.instructsIndex][I__DEPTH] == current_depth:

			#list element (brothers must be of the same kind)
			if data_isList:
				if instructs[_.instructsIndex][I__KEY] != '-':
					raise ValueError(
						"Key name '" + instructs[_.instructsIndex][I__KEY] + "' detected inside a list (line " + \
						str(instructs[_.instructsIndex][I__LINE_NBR]) + " column "                             + \
						str(instructs[_.instructsIndex][I__COLM_NBR]) + ")."
					)

				#add brother element next to the current one
				data.append(
					__getFullValue(
						instructs, current_depth,

						#characters
						comment_character    = comment_character,
						lineEnd_character    = lineEnd_character,
						newFile_character    = newFile_character,
						separation_character = separation_character,
						tabulation_character = tabulation_character,

						#options
						additionnalSpacesAllowed     = additionnalSpacesAllowed,
						debugMode                    = debugMode,
						externalImportationsAllowed  = externalImportationsAllowed,
						pythonCharactersOptimization = pythonCharactersOptimization
					)
				)

			#non-list element (brothers must be of the same kind)
			else:
				if instructs[_.instructsIndex][I__KEY] == '-':
					raise ValueError(
						"List element detected outside a list (line "              + \
						str(instructs[_.instructsIndex][I__LINE_NBR]) + " column " + \
						str(instructs[_.instructsIndex][I__COLM_NBR]) + ")."
					)
				key = instructs[_.instructsIndex][I__KEY]

				#check key before adding brother
				if key in data.keys():
					raise ValueError(
						"Key '" + key + "' already defined in its parent (line "   + \
						str(instructs[_.instructsIndex][I__LINE_NBR]) + " column " + \
						str(instructs[_.instructsIndex][I__COLM_NBR]) + ")."
					)

				#add brother element next to the current one (get value even recursively)
				data[key] = __getFullValue(
					instructs, current_depth,

					#characters
					comment_character    = comment_character,
					lineEnd_character    = lineEnd_character,
					newFile_character    = newFile_character,
					separation_character = separation_character,
					tabulation_character = tabulation_character,

					#options
					additionnalSpacesAllowed     = additionnalSpacesAllowed,
					debugMode                    = debugMode,
					externalImportationsAllowed  = externalImportationsAllowed,
					pythonCharactersOptimization = pythonCharactersOptimization
				)

		#case 4 : brother element of a parent (an uncle / grand-uncle / ...) => not of our business (end of child block)
		else:
			return data

	return data



#data -> to text
def __elementToText(
	elem,
	depth,

	#characters
	comment_character    = COMMENT_CHARACTER,
	lineEnd_character    = LINE_END_CHARACTER,
	newFile_character    = NEW_FILE_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
	tabulation_character = TABULATION_CHARACTER,

	#options
	additionnalSpacesAllowed     = ADDITIONAL_SPACES_ALLOWED,
	debugMode                    = DEBUG_MODE,
	externalImportationsAllowed  = EXTERNAL_IMPORTATIONS_ALLOWED,
	pythonCharactersOptimization = PYTHON_CHARACTERS_OPTIMIZATION
):
	'''
	[INTERNAL FUNCTION] Convert a data element into DREAMLANDS text.
	This function is recursive.

	data: dict, tuple, list
	depth: int

	Returns a chunk of DREAMLANDS text corresponding to the given data.
	'''
	newDepth = depth+1

	#case 1: [PARENT] element is a dictionnary
	if isinstance(elem, dict):
		text = lineEnd_character
		for k in elem.keys():
			text += newDepth*tabulation_character + k + separation_character + __elementToText(
				elem[k], newDepth,

				#characters
				comment_character    = comment_character,
				lineEnd_character    = lineEnd_character,
				newFile_character    = newFile_character,
				separation_character = separation_character,
				tabulation_character = tabulation_character,

				#options
				additionnalSpacesAllowed     = additionnalSpacesAllowed,
				debugMode                    = debugMode,
				externalImportationsAllowed  = externalImportationsAllowed,
				pythonCharactersOptimization = pythonCharactersOptimization
			)
		return text

	#case 2: [PARENT] element is a tuple/list
	elif isinstance(elem, tuple) or isinstance(elem, list):
		text = LINE_END_CHARACTER
		for e in elem:
			text += newDepth*tabulation_character + '-' + separation_character + __elementToText(
				e, newDepth,

				#characters
				comment_character    = comment_character,
				lineEnd_character    = lineEnd_character,
				newFile_character    = newFile_character,
				separation_character = separation_character,
				tabulation_character = tabulation_character,

				#options
				additionnalSpacesAllowed     = additionnalSpacesAllowed,
				debugMode                    = debugMode,
				externalImportationsAllowed  = externalImportationsAllowed,
				pythonCharactersOptimization = pythonCharactersOptimization
			)
		return text

	#case 3: [CHILD] element is standalone
	elif elem is not None:

		#special case 3.1: boolean
		if isinstance(elem, bool):
			if elem:
				return "true" + lineEnd_character
			return "false" + lineEnd_character

		#special case 3.2: strings
		elif isinstance(elem, str):

			#python characters optimization
			if pythonCharactersOptimization:
				if len(elem) == 1:
					return "\'" + str(elem) + "\'" + lineEnd_character
			return "\"" + str(elem) + "\"" + lineEnd_character

		#regular case 3.3: other [integer (including negative sign), floating point number (including negative sign)]
		return str(elem) + lineEnd_character

	#case 4: element is None => ERROR
	else:
		raise ValueError("Unable to parse DREAMLANDS text, data contains None value(s).")

def toText(
	data,

	#characters
	comment_character    = COMMENT_CHARACTER,
	lineEnd_character    = LINE_END_CHARACTER,
	newFile_character    = NEW_FILE_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
	tabulation_character = TABULATION_CHARACTER,

	#options
	additionnalSpacesAllowed     = ADDITIONAL_SPACES_ALLOWED,
	debugMode                    = DEBUG_MODE,
	externalImportationsAllowed  = EXTERNAL_IMPORTATIONS_ALLOWED,
	pythonCharactersOptimization = PYTHON_CHARACTERS_OPTIMIZATION
):
	'''
	Convert a data structure into DREAMLANDS text.

	data: dict, tuple, list

	Returns a DREAMLANDS text corresponding to the given data.
	'''

	#check structure type
	if not isinstance(data, dict) and not isinstance(data, tuple) and not isinstance(data, list):
		raise ValueError("Could not parse DREAMLANDS text, data has incorrect type (dict, tuple or list allowed).")

	#parse data
	return __elementToText(
		data, -1,

		#characters
		comment_character    = comment_character,
		lineEnd_character    = lineEnd_character,
		newFile_character    = newFile_character,
		separation_character = separation_character,
		tabulation_character = tabulation_character,

		#options
		additionnalSpacesAllowed     = additionnalSpacesAllowed,
		debugMode                    = debugMode,
		externalImportationsAllowed  = externalImportationsAllowed,
		pythonCharactersOptimization = pythonCharactersOptimization
	)[1:] #skip 1st character (useless LINE_END_CHARACTER in global context)






# ---- READ / WRITE ----

#read text from file => return data as dict
def read(
	filename,

	#characters
	comment_character    = COMMENT_CHARACTER,
	lineEnd_character    = LINE_END_CHARACTER,
	newFile_character    = NEW_FILE_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
	tabulation_character = TABULATION_CHARACTER,

	#options
	additionnalSpacesAllowed     = ADDITIONAL_SPACES_ALLOWED,
	debugMode                    = DEBUG_MODE,
	externalImportationsAllowed  = EXTERNAL_IMPORTATIONS_ALLOWED,
	pythonCharactersOptimization = PYTHON_CHARACTERS_OPTIMIZATION
):
	'''
	Read a DREAMLANDS file.

	filename: str

	Returns a dictionnary representing the data read from the file.
	'''

	#read text from file
	f = open(filename, "r")
	text = f.read()
	f.close()

	#parse
	return fromText(
		text,

		#characters
		comment_character    = comment_character,
		lineEnd_character    = lineEnd_character,
		newFile_character    = newFile_character,
		separation_character = separation_character,
		tabulation_character = tabulation_character,

		#options
		additionnalSpacesAllowed     = additionnalSpacesAllowed,
		debugMode                    = debugMode,
		externalImportationsAllowed  = externalImportationsAllowed,
		pythonCharactersOptimization = pythonCharactersOptimization
	)




#write data into file
def write(
	filename, data,

	#characters
	comment_character    = COMMENT_CHARACTER,
	lineEnd_character    = LINE_END_CHARACTER,
	newFile_character    = NEW_FILE_CHARACTER,
	separation_character = SEPARATION_CHARACTER,
	tabulation_character = TABULATION_CHARACTER,

	#options
	additionnalSpacesAllowed     = ADDITIONAL_SPACES_ALLOWED,
	debugMode                    = DEBUG_MODE,
	externalImportationsAllowed  = EXTERNAL_IMPORTATIONS_ALLOWED,
	pythonCharactersOptimization = PYTHON_CHARACTERS_OPTIMIZATION
):
	'''
	Write data into a DREAMLANDS file.

	filename: str
	data: dict

	Write the data respecting the DREAMLANDS syntax.
	'''

	#unparse
	text = toText(
		data,

		#characters
		comment_character    = comment_character,
		lineEnd_character    = lineEnd_character,
		newFile_character    = newFile_character,
		separation_character = separation_character,
		tabulation_character = tabulation_character,

		#options
		additionnalSpacesAllowed     = additionnalSpacesAllowed,
		debugMode                    = debugMode,
		externalImportationsAllowed  = externalImportationsAllowed,
		pythonCharactersOptimization = pythonCharactersOptimization
	)

	#write out
	f = open(filename, "w")
	f.write(text)
	f.close()

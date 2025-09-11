# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/defs.py

# -------- GENERAL --------

#option to be defined in src/main.z
deepDebug_stepByStep = False #should be a global VARIABLE dataitem

#general name parsing
NO_NAME            = -1
BLANK_AFTER_NAME   = -2
NOTHING_AFTER_NAME = -3

#root types
ROOT_TYPES = (
	"boo",
	"s1", "u1",
	"s2", "u2",
	"s4", "u4",
	"s8", "u8",
	"f4", "f8",
	"ptr"
)
RT__BOO = 0 #enm #for indexing in zCtx.rootTypes
RT__S1  = 1
RT__U1  = 2
RT__S2  = 3
RT__U2  = 4
RT__S4  = 5
RT__U4  = 6
RT__S8  = 7
RT__U8  = 8
RT__F4  = 9
RT__F8  = 10
RT__PTR = 11

#specific type ID
TYPE_ID__NOT_FOUND = 0

#common data structures (shortcut notations)
TYPE_FULLNAME__TAB  = "GUtab"
TYPE_FULLNAME__LST  = "GUlst"
TYPE_FULLNAME__FLY  = "GUfly"
TYPE_FULLNAME__FMAP = "GUfmap"
TYPE_FULLNAME__MMAP = "GUmmap"

#byte notations
BN_PREFIX = '`'

#literal numeric values: binary limits
MAX_BINARY_DIGITS_ALLOWED__U2 = 16
MAX_BINARY_DIGITS_ALLOWED__U4 = 32
MAX_BINARY_DIGITS_ALLOWED__U8 = 64

#literal numeric values: octal limits
MAX_OCTAL_DIGITS_ALLOWED__U2 = 6
MAX_OCTAL_DIGITS_ALLOWED__U4 = 12
MAX_OCTAL_DIGITS_ALLOWED__U8 = 24

#literal numeric values: hexadecimal limits
MAX_BINARY_DIGITS_ALLOWED__U2 = 4
MAX_BINARY_DIGITS_ALLOWED__U4 = 8
MAX_BINARY_DIGITS_ALLOWED__U8 = 16

#literal numeric values: signed decimal limits
MAX_DECIMAL_DIGITS_ALLOWED__S2 = 5
MAX_DECIMAL_DIGITS_ALLOWED__S4 = 10
MAX_DECIMAL_DIGITS_ALLOWED__S8 = 19

#literal numeric values: unsigned decimal limits
MAX_DECIMAL_DIGITS_ALLOWED__U2 = 5
MAX_DECIMAL_DIGITS_ALLOWED__U4 = 10
MAX_DECIMAL_DIGITS_ALLOWED__U8 = 20

#Single Operators
SYMBOL__SIN = 1 #invert
SYMBOL__SNO = 2 #not
SO = (SYMBOL__SIN, SYMBOL__SNO)

#Decisionnal Operators
SYMBOL__DAN = 3 #decisionnal and
SYMBOL__DOR = 4 #decisionnal or
DO = (SYMBOL__DAN, SYMBOL__DOR)

#Arithmetic Operators
SYMBOL__AMU = 5 #multiply
SYMBOL__ADI = 6 #divide
SYMBOL__AMO = 7 #modulo
SYMBOL__APO = 8 #power
AO = (SYMBOL__AMU, SYMBOL__ADI, SYMBOL__AMO, SYMBOL__APO)

#B-rithmetic Operators
SYMBOL__BAD =  9 #add
SYMBOL__BSU = 10 #subtract
BO = (SYMBOL__BAD, SYMBOL__BSU)

#Logical Operators
SYMBOL__LAN = 11 #logical and
SYMBOL__LOR = 12 #logical or
SYMBOL__LXO = 13 #logical xor
SYMBOL__LLS = 14 #left shift
SYMBOL__LRS = 15 #right shift
SYMBOL__LLB = 16 #left byte-shift
SYMBOL__LRB = 17 #right byte-shift
SYMBOL__LLR = 18 #left roll
SYMBOL__LRR = 19 #right roll
LO = (
	SYMBOL__LAN, SYMBOL__LOR, SYMBOL__LXO,
	SYMBOL__LLS, SYMBOL__LRS,
	SYMBOL__LLB, SYMBOL__LRB,
	SYMBOL__LLR, SYMBOL__LRR
)

#Conditionnal Operators
SYMBOL__CEQ = 20 #equals
SYMBOL__CNE = 21 #not equals
SYMBOL__CLT = 22 #lesser than
SYMBOL__CGT = 23 #greater than
SYMBOL__CLE = 24 #lesser or equal
SYMBOL__CGE = 25 #greater or equal
CO = (
	SYMBOL__CEQ, SYMBOL__CNE,
	SYMBOL__CLT, SYMBOL__CGT,
	SYMBOL__CLE, SYMBOL__CGE
)

#Indexing Operators (without includers)
SYMBOL__IAM = 30 #among
SYMBOL__INA = 31 #not among
IO_AMONG = (SYMBOL__IAM, SYMBOL__INA)

#Fixed Operators
SYMBOL__FSZ = 32 #size
SYMBOL__FRF = 33 #reference
SYMBOL__FCA = 34 #casht
SYMBOL__FFA = 35 #field access

#mono-operand operators
MONO_OPERAND = SO + (SYMBOL__FSZ, SYMBOL__FRF)

#other
SYMBOL__ASG       = 1 #assignment
SYMBOL__NOT_FOUND = 0

#lengths
SYMBOL_LENGTHS = { #map[ubyt,ubyt]
	SYMBOL__SIN: 1, SYMBOL__SNO: 1, SYMBOL__DAN: 2, SYMBOL__DOR: 2,
	SYMBOL__AMU: 1, SYMBOL__ADI: 1, SYMBOL__AMO: 1, SYMBOL__APO: 2,
	SYMBOL__BAD: 1, SYMBOL__BSU: 1, SYMBOL__LAN: 1, SYMBOL__LOR: 1,
	SYMBOL__LXO: 1, SYMBOL__LLS: 2, SYMBOL__LRS: 2, SYMBOL__LLB: 3,
	SYMBOL__LRB: 3, SYMBOL__LLR: 3, SYMBOL__LRR: 3, SYMBOL__CEQ: 2,
	SYMBOL__CNE: 2, SYMBOL__CLT: 1, SYMBOL__CGT: 1, SYMBOL__CLE: 2,
	SYMBOL__CGE: 2, SYMBOL__IAM: 2, SYMBOL__INA: 3, SYMBOL__FSZ: 1,
	SYMBOL__FRF: 1, SYMBOL__FCA: 1, SYMBOL__FFA: 1, SYMBOL__ASG: 1,
	SYMBOL__NOT_FOUND: 0
}
OPERATOR_NAMES = {
	SYMBOL__SIN: "sin", SYMBOL__SNO: "sno", SYMBOL__DAN: "dan", SYMBOL__DOR: "dor",
	SYMBOL__AMU: "amu", SYMBOL__ADI: "adi", SYMBOL__AMO: "amo", SYMBOL__APO: "apo",
	SYMBOL__BAD: "bad", SYMBOL__BSU: "bsu", SYMBOL__LAN: "lan", SYMBOL__LOR: "lor",
	SYMBOL__LXO: "lxo", SYMBOL__LLS: "lls", SYMBOL__LRS: "lrs", SYMBOL__LLB: "llb",
	SYMBOL__LRB: "lrb", SYMBOL__LLR: "llr", SYMBOL__LRR: "lrr", SYMBOL__CEQ: "ceq",
	SYMBOL__CNE: "cne", SYMBOL__CLT: "clt", SYMBOL__CGT: "cgt", SYMBOL__CLE: "cle",
	SYMBOL__CGE: "cge", SYMBOL__IAM: "iam", SYMBOL__INA: "ina", SYMBOL__FSZ: "fsz",
	SYMBOL__FRF: "frf", SYMBOL__FCA: "fca", SYMBOL__FFA: "ffa"
}
FO_NAMES = (
	OPERATOR_NAMES[SYMBOL__FSZ], OPERATOR_NAMES[SYMBOL__FRF],
	OPERATOR_NAMES[SYMBOL__FCA], OPERATOR_NAMES[SYMBOL__FFA]
)

#general syntax
BLANKS          = (' ', '\t')
BLANKS_EXTENDED = (' ', '\t', '\n')
INCLUDERS       = { '(':')', '[':']', '{':'}' }

#charsets
DEFAULT_NAME_CHARSET              = tuple(string.ascii_letters + string.digits + '_')
ZCI_FIRSTWORD_DETECTION_BLACKLIST = BLANKS + tuple(INCLUDERS.keys())
FCT_NAME_BLACKLIST                = BLANKS + ('(',)
FCT_NAME_CHARSET                  = DEFAULT_NAME_CHARSET + ('.', '[', ']', '=', '-', '+', '*', '/', '^', '%', ':', '~', '!', '?', '&', '|', '<', '>')
VALUE_CHARSET                     = FCT_NAME_CHARSET + ZCI_FIRSTWORD_DETECTION_BLACKLIST + ('@', '#', '$', '`') #additionnal FO + byte notation prefix

#cpl opt set
CPL_OPT_VALUES__ARCH  = 0 #architecture type
CPL_OPT_VALUES__ONOFF = 1
CPL_OPT_VALUES__DIGIT = 2
CPL_OPT_VALUES__RTYPE = 3 #root type
CPL_OPT_ALLOWED = {
	"ARCH":                           CPL_OPT_VALUES__ARCH,
	"INTERPRET_COMMON_STRUCTURES":    CPL_OPT_VALUES__ONOFF,
	"MAX_INSTRUCTS_NOFUNCTION":       CPL_OPT_VALUES__DIGIT,
	"CHECK_NULL_STC_BEFORE_METHOD":   CPL_OPT_VALUES__ONOFF,
	"OPERATORS_SUPPORTS_INHERITANCE": CPL_OPT_VALUES__ONOFF,
	"METHODS_SUPPORTS_INHERITANCE":   CPL_OPT_VALUES__ONOFF,
	"EMPTY_DATA_ITEM_NULL":           CPL_OPT_VALUES__ONOFF,
	"UNDECLINATED_IMPLICITSOURCE":    CPL_OPT_VALUES__RTYPE,
	"LS_CNT_DIGITS":                  CPL_OPT_VALUES__DIGIT
}

#data item nature
NATURE__PRIMITIVE = 0
NATURE__STRUCTURE = 1
NATURE__ENUMERATE = 2

#statement kinds
STM__IF_ = 0
STM__FOR = 1
STM__WHI = 2
STM__SWI = 3

#pcpl items
PCPL_ITEM_NAME_CHARSET = DEFAULT_NAME_CHARSET #no link, but same value








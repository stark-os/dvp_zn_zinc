# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> zctx/defs.py

# -------- GENERAL --------

#current step <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<< SHOULD BE GBL CST ENM
class Step:
	def __init__(sbj):
		sbj.INIT = 0
		sbj.P1   = 1
		sbj.P2   = 2
		sbj.P3   = 3
		sbj.C01  = 4
		sbj.C02  = 5
		sbj.C03  = 6
STEP = Step()

#general name parsing
NO_NAME            = -1
BLANK_AFTER_NAME   = -2
NOTHING_AFTER_NAME = -3

#root types
ROOT_TYPES = (
	"boo",
	"s8",  "u8",
	"s16", "u16",
	"s32", "u32",
	"s64", "u64",
	"f32", "f64",
	"ref"
)
RT__BOO = 0 #enm #for indexing in zCtx.rootTypes
RT__S8  = 1
RT__U8  = 2
RT__S16 = 3
RT__U16 = 4
RT__S32 = 5
RT__U32 = 6
RT__S64 = 7
RT__U64 = 8
RT__F32 = 9
RT__F64 = 10
RT__REF = 11

#specific type ID
TYPE_ID__UNKNOWN = -1

#common data structures (shortcut notations)
TYPE_FULLNAME__TAB  = "GUtab"
TYPE_FULLNAME__LST  = "GUlst"
TYPE_FULLNAME__FLY  = "GUfly"
TYPE_FULLNAME__FMAP = "GUfmap"
TYPE_FULLNAME__MMAP = "GUmmap"

#byte notations
BN_PFX = '`'

#literal numeric values: binary limits
MAX_BINARY_DIGITS_ALLOWED__U16 = 16
MAX_BINARY_DIGITS_ALLOWED__U32 = 32
MAX_BINARY_DIGITS_ALLOWED__U64 = 64

#literal numeric values: octal limits
MAX_OCTAL_DIGITS_ALLOWED__U16 = 6
MAX_OCTAL_DIGITS_ALLOWED__U32 = 12
MAX_OCTAL_DIGITS_ALLOWED__U64 = 24

#literal numeric values: hexadecimal limits
MAX_BINARY_DIGITS_ALLOWED__U16 = 4
MAX_BINARY_DIGITS_ALLOWED__U32 = 8
MAX_BINARY_DIGITS_ALLOWED__U64 = 16

#literal numeric values: signed decimal limits
MAX_DECIMAL_DIGITS_ALLOWED__S16 = 5
MAX_DECIMAL_DIGITS_ALLOWED__S32 = 10
MAX_DECIMAL_DIGITS_ALLOWED__S64 = 19

#literal numeric values: unsigned decimal limits
MAX_DECIMAL_DIGITS_ALLOWED__U16 = 5
MAX_DECIMAL_DIGITS_ALLOWED__U32 = 10
MAX_DECIMAL_DIGITS_ALLOWED__U64 = 20

#other
SYMBOL__ASG       = 1 #assignment
SYMBOL__NOT_FOUND = 0

#Single Operators
SYMBOL__SIN = 1 #invert
SYMBOL__SNO = 2 #not

#Decisionnal Operators
SYMBOL__DAN = 3 #decisionnal and
SYMBOL__DOR = 4 #decisionnal or

#Arithmetic Operators
SYMBOL__AMU = 5 #multiply
SYMBOL__ADI = 6 #divide
SYMBOL__AMO = 7 #modulo
SYMBOL__APO = 8 #power

#B-rithmetic Operators
SYMBOL__BAD =  9 #add
SYMBOL__BSU = 10 #subtract

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

#Conditionnal Operators
SYMBOL__CEQ = 20 #equals
SYMBOL__CNE = 21 #not equals
SYMBOL__CLT = 22 #lesser than
SYMBOL__CGT = 23 #greater than
SYMBOL__CLE = 24 #lesser or equal
SYMBOL__CGE = 25 #greater or equal

#Indexing Operators
SYMBOL__IAM = 30 #among
SYMBOL__INA = 31 #not among
SYMBOL__IIN = 32 #index
SYMBOL__IIA = 33 #index assign
SYMBOL__ISU = 34 #sub
SYMBOL__ISA = 35 #sub assign

#Fixed Operators
SYMBOL__FSZ = 36 #size
SYMBOL__FRF = 37 #reference
SYMBOL__FCA = 38 #casht
SYMBOL__FFA = 39 #field access

#useful symbol sets
SO = (SYMBOL__SIN, SYMBOL__SNO)
DO = (SYMBOL__DAN, SYMBOL__DOR)
AO = (
	SYMBOL__AMU, SYMBOL__ADI,
	SYMBOL__AMO, SYMBOL__APO
)
BO = (SYMBOL__BAD, SYMBOL__BSU)
LO = (
	SYMBOL__LAN, SYMBOL__LOR, SYMBOL__LXO,
	SYMBOL__LLS, SYMBOL__LRS,
	SYMBOL__LLB, SYMBOL__LRB,
	SYMBOL__LLR, SYMBOL__LRR
)
CO = (
	SYMBOL__CEQ, SYMBOL__CNE,
	SYMBOL__CLT, SYMBOL__CGT,
	SYMBOL__CLE, SYMBOL__CGE
)
IO_AMONG     = (SYMBOL__IAM, SYMBOL__INA)
MONO_OPERAND = SO + (SYMBOL__FSZ, SYMBOL__FRF)

#operator names in DCL_FCT
OPERATOR_FCTNAME2SYMBOL = {
	"~"  : SYMBOL__SIN, "!"   : SYMBOL__SNO, #SO
	"&&" : SYMBOL__DAN, "||"  : SYMBOL__DOR, #DO
	"*"  : SYMBOL__AMU, "/"   : SYMBOL__ADI, #AO
	"%"  : SYMBOL__AMO, "**"  : SYMBOL__APO,
	"+"  : SYMBOL__BAD, "-"   : SYMBOL__BSU, #BO
	"&"  : SYMBOL__LAN, "|"   : SYMBOL__LOR, "^": SYMBOL__LXO, #LO
	"<<" : SYMBOL__LLS, ">>"  : SYMBOL__LRS,
	"<<|": SYMBOL__LLB, "|>>" : SYMBOL__LRB,
	"<<-": SYMBOL__LLR, "->>" : SYMBOL__LRR,
	"==" : SYMBOL__CEQ, "!="  : SYMBOL__CNE, #CO
	"<"  : SYMBOL__CLT, ">"   : SYMBOL__CGT,
	"<=" : SYMBOL__CLE, ">="  : SYMBOL__CGE,
	"?"  : SYMBOL__IAM, "!?"  : SYMBOL__INA, #IO
	"[]" : SYMBOL__IIN, "[]=" : SYMBOL__IIA,
	"[:]": SYMBOL__ISU, "[:]=": SYMBOL__ISA
}

#lengths
SYMBOL_LENGTHS = { #map[ubyt,ubyt]
	SYMBOL__SIN: 1, SYMBOL__SNO: 1, #SO
	SYMBOL__DAN: 2, SYMBOL__DOR: 2, #DO
	SYMBOL__AMU: 1, SYMBOL__ADI: 1,
	SYMBOL__AMO: 1, SYMBOL__APO: 2, #AO
	SYMBOL__BAD: 1, SYMBOL__BSU: 1, #BO
	SYMBOL__LAN: 1, SYMBOL__LOR: 1, SYMBOL__LXO: 1, #LO
	SYMBOL__LLS: 2, SYMBOL__LRS: 2,
	SYMBOL__LLB: 3, SYMBOL__LRB: 3,
	SYMBOL__LLR: 3, SYMBOL__LRR: 3,
	SYMBOL__CEQ: 2, SYMBOL__CNE: 2, #CO
	SYMBOL__CLT: 1, SYMBOL__CGT: 1,
	SYMBOL__CLE: 2, SYMBOL__CGE: 2,
	SYMBOL__IAM: 2, SYMBOL__INA: 3, #IO
	SYMBOL__FSZ: 1, SYMBOL__FRF: 1, #FO
	SYMBOL__FCA: 1, SYMBOL__FFA: 1,
	SYMBOL__ASG: 1,	SYMBOL__NOT_FOUND: 0 #other
}
OPERATOR_NAMES = {
	SYMBOL__SIN: "sin", SYMBOL__SNO: "sno", #SO
	SYMBOL__DAN: "dan", SYMBOL__DOR: "dor", #DO
	SYMBOL__AMU: "amu", SYMBOL__ADI: "adi", #AO
	SYMBOL__AMO: "amo", SYMBOL__APO: "apo",
	SYMBOL__BAD: "bad", SYMBOL__BSU: "bsu", #BO
	SYMBOL__LAN: "lan", SYMBOL__LOR: "lor", SYMBOL__LXO: "lxo", #LO
	SYMBOL__LLS: "lls", SYMBOL__LRS: "lrs",
	SYMBOL__LLB: "llb", SYMBOL__LRB: "lrb",
	SYMBOL__LLR: "llr", SYMBOL__LRR: "lrr",
	SYMBOL__CEQ: "ceq", SYMBOL__CNE: "cne", #CO
	SYMBOL__CLT: "clt", SYMBOL__CGT: "cgt",
	SYMBOL__CLE: "cle", SYMBOL__CGE: "cge",
	SYMBOL__IAM: "iam", SYMBOL__INA: "ina", #IO
	SYMBOL__IIN: "iin", SYMBOL__IIA: "iia",
	SYMBOL__ISU: "isu", SYMBOL__ISA: "isa",
	SYMBOL__FSZ: "fsz", SYMBOL__FRF: "frf", #FO
	SYMBOL__FCA: "fca", SYMBOL__FFA: "ffa"
}

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

#data item nature
NATURE__PRM = 0
NATURE__STC = 1
NATURE__ENM = 2

#statement kinds
STM__IF  = 0
STM__FOR = 1
STM__WHI = 2
STM__SWI = 3

#cpl opt set
CPL_OPT__VALUES__ARCH  = 0 #architecture type
CPL_OPT__VALUES__ONOFF = 1
CPL_OPT__VALUES__DIGIT = 2
CPL_OPT__VALUES__RTYPE = 3 #root type
CPL_OPT__ALLOWED = {
	"ARCH":                           CPL_OPT__VALUES__ARCH,
	"INTERPRET_COMMON_STRUCTURES":    CPL_OPT__VALUES__ONOFF,
	"MAX_INSTRUCTS_NOFUNCTION":       CPL_OPT__VALUES__DIGIT,
	"CHECK_NULL_STC_BEFORE_METHOD":   CPL_OPT__VALUES__ONOFF,
	"OPERATORS_SUPPORTS_INHERITANCE": CPL_OPT__VALUES__ONOFF,
	"METHODS_SUPPORTS_INHERITANCE":   CPL_OPT__VALUES__ONOFF,
	"EMPTY_DATA_ITEM_NULL":           CPL_OPT__VALUES__ONOFF,
	"UNDECLINATED_IMPLICITSOURCE":    CPL_OPT__VALUES__RTYPE,
	"LS_CNT_DIGITS":                  CPL_OPT__VALUES__DIGIT
}

#pcpl items
PCPL__ITEM_NAME_CHARSET         = DEFAULT_NAME_CHARSET #no link, but same value
PCPL__DIRECTIVES_MAX_COMPLEXITY = 10









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
	"f32", "f64"
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
#RT__STC = 11

#specific type ID
TYPE_ID__UNKNOWN = -1

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
MAX_HEXADECIMAL_DIGITS_ALLOWED__U16 = 4
MAX_HEXADECIMAL_DIGITS_ALLOWED__U32 = 8
MAX_HEXADECIMAL_DIGITS_ALLOWED__U64 = 16

#literal numeric values: signed decimal limits
MAX_DECIMAL_DIGITS_ALLOWED__S16 = 5
MAX_DECIMAL_DIGITS_ALLOWED__S32 = 10
MAX_DECIMAL_DIGITS_ALLOWED__S64 = 19

#literal numeric values: unsigned decimal limits
MAX_DECIMAL_DIGITS_ALLOWED__U16 = 5
MAX_DECIMAL_DIGITS_ALLOWED__U32 = 10
MAX_DECIMAL_DIGITS_ALLOWED__U64 = 20

#other
SYM__ASG       = 1 #assignment
SYM__NOT_FOUND = 0

#Single Operators
SYM__SIN = 1 #invert
SYM__SNO = 2 #not

#Decisionnal Operators
SYM__DAN = 3 #decisionnal and
SYM__DOR = 4 #decisionnal or

#Arithmetic Operators
SYM__AMU = 5 #multiply
SYM__ADI = 6 #divide
SYM__AMO = 7 #modulo
SYM__APO = 8 #power

#B-rithmetic Operators
SYM__BAD =  9 #add
SYM__BSU = 10 #subtract

#Logical Operators
SYM__LAN = 11 #logical and
SYM__LOR = 12 #logical or
SYM__LXO = 13 #logical xor
SYM__LLS = 14 #left shift
SYM__LRS = 15 #right shift
SYM__LLB = 16 #left byte-shift
SYM__LRB = 17 #right byte-shift
SYM__LLR = 18 #left roll
SYM__LRR = 19 #right roll

#Conditionnal Operators
SYM__CEQ = 20 #equals
SYM__CNE = 21 #not equals
SYM__CLT = 22 #lesser than
SYM__CGT = 23 #greater than
SYM__CLE = 24 #lesser or equal
SYM__CGE = 25 #greater or equal

#Indexing Operators
SYM__IAM = 30 #among
SYM__INA = 31 #not among
SYM__IIN = 32 #index
SYM__IIA = 33 #index assign
SYM__ISU = 34 #sub
SYM__ISA = 35 #sub assign

#Fixed Operators
SYM__FSZ = 36 #size
SYM__FRF = 37 #reference
SYM__FCA = 38 #casht
SYM__FFA = 39 #field access

#useful symbol sets
SO = (SYM__SIN, SYM__SNO)
DO = (SYM__DAN, SYM__DOR)
AO = (
	SYM__AMU, SYM__ADI,
	SYM__AMO, SYM__APO
)
BO = (SYM__BAD, SYM__BSU)
LO = (
	SYM__LAN, SYM__LOR, SYM__LXO,
	SYM__LLS, SYM__LRS,
	SYM__LLB, SYM__LRB,
	SYM__LLR, SYM__LRR
)
CO = (
	SYM__CEQ, SYM__CNE,
	SYM__CLT, SYM__CGT,
	SYM__CLE, SYM__CGE
)
IO_AMONG     = (SYM__IAM, SYM__INA)
MONO_OPERAND = SO + (SYM__FSZ, SYM__FRF)

#operator names in DCL_FCT
OPERATOR_FCTNAME2SYMBOL = {
	"~"  : SYM__SIN, "!"   : SYM__SNO, #SO
	"&&" : SYM__DAN, "||"  : SYM__DOR, #DO
	"*"  : SYM__AMU, "/"   : SYM__ADI, #AO
	"%"  : SYM__AMO, "**"  : SYM__APO,
	"+"  : SYM__BAD, "-"   : SYM__BSU, #BO
	"&"  : SYM__LAN, "|"   : SYM__LOR, "^": SYM__LXO, #LO
	"<<" : SYM__LLS, ">>"  : SYM__LRS,
	"|<<": SYM__LLB, ">>|" : SYM__LRB,
	"<<-": SYM__LLR, "->>" : SYM__LRR,
	"==" : SYM__CEQ, "!="  : SYM__CNE, #CO
	"<"  : SYM__CLT, ">"   : SYM__CGT,
	"<=" : SYM__CLE, ">="  : SYM__CGE,
	"?"  : SYM__IAM, "!?"  : SYM__INA, #IO
	"[]" : SYM__IIN, "[]=" : SYM__IIA,
	"[:]": SYM__ISU, "[:]=": SYM__ISA
}

#lengths
SYM_LENGTHS = { #map[ubyt,ubyt]
	SYM__SIN: 1, SYM__SNO: 1, #SO
	SYM__DAN: 2, SYM__DOR: 2, #DO
	SYM__AMU: 1, SYM__ADI: 1,
	SYM__AMO: 1, SYM__APO: 2, #AO
	SYM__BAD: 1, SYM__BSU: 1, #BO
	SYM__LAN: 1, SYM__LOR: 1, SYM__LXO: 1, #LO
	SYM__LLS: 2, SYM__LRS: 2,
	SYM__LLB: 3, SYM__LRB: 3,
	SYM__LLR: 3, SYM__LRR: 3,
	SYM__CEQ: 2, SYM__CNE: 2, #CO
	SYM__CLT: 1, SYM__CGT: 1,
	SYM__CLE: 2, SYM__CGE: 2,
	SYM__IAM: 2, SYM__INA: 3, #IO
	SYM__FSZ: 1, SYM__FRF: 1, #FO
	SYM__FCA: 1, SYM__FFA: 1,
	SYM__ASG: 1,	SYM__NOT_FOUND: 0 #other
}
OPE_NAMES = {
	SYM__SIN: "sin", SYM__SNO: "sno", #SO
	SYM__DAN: "dan", SYM__DOR: "dor", #DO
	SYM__AMU: "amu", SYM__ADI: "adi", #AO
	SYM__AMO: "amo", SYM__APO: "apo",
	SYM__BAD: "bad", SYM__BSU: "bsu", #BO
	SYM__LAN: "lan", SYM__LOR: "lor", SYM__LXO: "lxo", #LO
	SYM__LLS: "lls", SYM__LRS: "lrs",
	SYM__LLB: "llb", SYM__LRB: "lrb",
	SYM__LLR: "llr", SYM__LRR: "lrr",
	SYM__CEQ: "ceq", SYM__CNE: "cne", #CO
	SYM__CLT: "clt", SYM__CGT: "cgt",
	SYM__CLE: "cle", SYM__CGE: "cge",
	SYM__IAM: "iam", SYM__INA: "ina", #IO
	SYM__IIN: "iin", SYM__IIA: "iia",
	SYM__ISU: "isu", SYM__ISA: "isa",
	SYM__FSZ: "fsz", SYM__FRF: "frf", #FO
	SYM__FCA: "fca", SYM__FFA: "ffa"
}
MONO_OPERAND_NAMES = (
	"sin", "sno", #SO
	"fsz", "frf"  #FO
)

#general syntax
BLANKS          = (' ', '\t')
BLANKS_EXTENDED = (' ', '\t', '\n')
INCLUDERS       = { '(':')', '[':']', '{':'}' }

#charsets
DEFAULT_NAME_CHARSET              = tuple(string.ascii_letters + string.digits + '_')
ZCI_FIRSTWORD_DETECTION_BLACKLIST = BLANKS + tuple(INCLUDERS.keys())
FCT_NAME_BLACKLIST                = BLANKS + ('(',)
FCT_NAME_CHARSET                  = DEFAULT_NAME_CHARSET + (
	'-', '+', '*', '/', '%', #A/BO
	'^', '&', '|', '~',      #LO
	'?', '[', ']', ':',      #IO
	'=', '<', '>',           #CO
	'!', '.'                 #other
)
VALUE_CHARSET = BLANKS + tuple(INCLUDERS.keys()) + DEFAULT_NAME_CHARSET + (
	'-', '+', '*', '/', '%', #A/BO
	'^', '&', '|', '~',      #LO
	'?', ':',                #IO
	'=', '<', '>',           #CO
	'.', '@', '#', '$', '`', #FO + byte notation prefix
	'!'                      #other
)

#data item nature
NATURE__PRM = 0
NATURE__STC = 1
NATURE__ENM = 2

#jump kinds
JMP__BRK = 0
JMP__CTN = 1
JMP__RET = 2

#cpl info
CPL__MODE_EXE  = 0
CPL__MODE_SDL  = 1
CPL__MODE_MASK = 1
CPL__USE_REF_ALLOWED   = 0
CPL__USE_REF_FORBIDDEN = 2
CPL__USE_REF_MASK      = 2

#cpl opt set
CPL_OPT__VALUES__ARCH  = 0 #architecture type
CPL_OPT__VALUES__FILE  = 1
CPL_OPT__VALUES__ONOFF = 2
CPL_OPT__VALUES__DIGIT = 3
CPL_OPT__VALUES__RTYPE = 4 #root type
CPL_OPT__ALLOWED = {
	"ARCH":                         CPL_OPT__VALUES__ARCH,
	"LLI_FP_PATH":                  CPL_OPT__VALUES__FILE,
	"DEFAULT_ACCESS_PUB":           CPL_OPT__VALUES__ONOFF,
	"COMMON_STC_SHORTCUTS":         CPL_OPT__VALUES__ONOFF,
	"MAX_INSTRUCTS_NOFCT":          CPL_OPT__VALUES__DIGIT,
	"CHECK_NULL_STC_BEFORE_METHOD": CPL_OPT__VALUES__ONOFF,
	"OPES_SUPPORTS_INHERITANCE":    CPL_OPT__VALUES__ONOFF,
	"METHODS_SUPPORTS_INHERITANCE": CPL_OPT__VALUES__ONOFF,
	"EMPTY_DATA_ITEM_NULL":         CPL_OPT__VALUES__ONOFF,
	"UNDCN_IMPLICITSOURCE":         CPL_OPT__VALUES__RTYPE,
	"DCN_NBR_MAX":                  CPL_OPT__VALUES__DIGIT,
	"LS_CNT_DIGITS":                CPL_OPT__VALUES__DIGIT
}

#pcpl items
PCPL__NAME_CHARSET                  = DEFAULT_NAME_CHARSET #no link, but same value
PCPL__DIRECTIVES_MAX_COMPLEXITY     = 10
PCPL__DIRECTIVES_MAX_COMPLEXITY_KEY = "DIRECTIVES_MAX_COMPLEXITY_LEVEL"







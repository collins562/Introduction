"""The vm_definitions module provides type define of instructions, segments
and registers, and functions for detecting constant, segments or instructions. 
"""

# Command types
C_ERROR      = 0
C_ARITHMETIC = 1
C_PUSH       = 2
C_POP        = 3
C_LABEL      = 4
C_GOTO       = 5
C_IF         = 6
C_FUNCTION   = 7
C_CALL       = 8
C_RETURN     = 9

# Segment names
S_LCL        = 'local'
S_ARG        = 'argument'
S_THIS       = 'this'
S_THAT       = 'that'
S_PTR        = 'pointer'
S_TEMP       = 'temp'
S_CONST      = 'constant'
S_STATIC     = 'static'

# Registers
R_R0  = R_SP    = 0
R_R1  = R_LCL   = 1
R_R2  = R_ARG   = 2
R_R3  = R_THIS  = R_PTR = 3
R_R4  = R_THAT  = 4
R_R5  = R_TEMP  = 5
R_R6            = 6
R_R7            = 7
R_R8            = 8
R_R9            = 9
R_R10           = 10
R_R11           = 11
R_R12           = 12
R_R13 = R_FRAME = 13
R_R14 = R_RET   = 14
R_R15 = R_COPY  = 15

# mappings
ARITH_INST   = ('add', 'sub', 'neg', 'eq' , 'gt', 'lt', 'and', 'or', 'not')
STACK_INST   = {'pop': C_POP, 'push': C_PUSH}
PROG_INST    = {'label': C_LABEL, 'goto': C_GOTO, 'if-goto': C_IF}
FUNC_INST    = {'function': C_FUNCTION, 'call': C_CALL, 'return': C_RETURN}
MEMO_SEG     = (S_LCL, S_ARG, S_THIS, S_THAT)
REG_SEG      = (S_PTR, S_TEMP)
STATIC_SEG   = (S_STATIC,)
CONST_SEG    = (S_CONST,)
SEGMENTS     = MEMO_SEG + REG_SEG + STATIC_SEG + CONST_SEG
MEMO_SYMBOLS = {S_LCL: 'LCL', S_ARG: 'ARG', S_THIS: 'THIS', S_THAT: 'THAT'}
REG_ADDRESS  = {S_PTR: R_THIS, S_TEMP: R_TEMP}

def is_const(s):
    return s.isdigit()

def is_segment(s):
    return s in SEGMENTS

def is_memo_seg(s):
    return s in MEMO_SEG

def is_reg_seg(s):
    return s in REG_SEG

def is_static_seg(s):
    return s in STATIC_SEG

def is_const_seg(s):
    return s in CONST_SEG

def is_stack_inst(s):
    return s in STACK_INST

def is_arith_inst(s):
    return s in ARITH_INST

def is_prog_inst(s):
    return s in PROG_INST

def is_func_inst(s):
    return s in FUNC_INST

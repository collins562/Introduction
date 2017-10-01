"""The vm_primitives module provides type define of instructions, segments
and registers, and check functions for the commands in the vm files. A 
command is a tokenized list which may be preceded by:

  * stack instruction
  * arithmetic instruction
  * program flow instruction
  * function instruction

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

def vm_const(s):
    return s.isdigit()

def vm_seg(s):
    return s in SEGMENTS

def vm_memo_seg(s):
    return s in MEMO_SEG

def vm_reg_seg(s):
    return s in REG_SEG

def vm_static_seg(s):
    return s in STATIC_SEG

def vm_const_seg(s):
    return s in CONST_SEG

def vm_stack_inst(s):
    return s in STACK_INST

def vm_arith_inst(s):
    return s in ARITH_INST

def vm_prog_inst(s):
    return s in PROG_INST

def vm_func_inst(s):
    return s in FUNC_INST

def check_command(command):
    """Check command format. Return:
        * (C_ERROR, message) if there is an error or
        * (int, None) if there isn't
    """
    tag = command[0]
    if vm_stack_inst(tag):
        return check_stack(command)
    elif vm_arith_inst(tag):
        return check_arith(command)
    elif vm_prog_inst(tag):
        return check_prog(command)
    elif vm_func_inst(tag):
        return check_func(command)
    else:
        return C_ERROR, "Illegal instruction: " + tag

def check_arith(command):
    """arithmetic format: <inst>"""
    if len(command) > 1:
        return C_ERROR, "Unexpected arguments: " + ' '.join(command[1:])
    return C_ARITHMETIC, None

def check_stack(command):
    """stack format: <inst> <segment> <constant>"""
    me = None
    if len(command) < 3:
        me = "Too few arguments."
    elif len(command) > 3:
        me = "Too many arguments"
    elif not vm_seg(command[1]):
        me = "Except a segment not: " + command[1]
    elif not vm_const(command[2]):
        me = "Except a constant not: " + command[2]
    elif command[0] == 'pop' and command[1] == S_CONST:
        me = "Cannot pop to a constant"
    elif command[1] == S_PTR and int(command[2]) > 1:
        me = "segment out of range: pointer 0-1"
    elif command[1] == S_TEMP and int(command[2]) > 7:
        me = "segment out of range: temp 0-7"
    return C_ERROR if me else STACK_INST[command[0]], me

def check_prog(command):
    """program flow format: <inst> <symbol>"""
    me = None
    if len(command) < 2:
        me = "Except a label."
    elif len(command) > 2:
        me = "Too many arguments."
    return C_ERROR if me else PROG_INST[command[0]], me

def check_func(command):
    """function format:
    function: function <symbol> <constant>
        call: call <sumbol> <constant>
      return: return
    """
    me = None
    if command[0] == 'return':
        if len(command) > 1:
            me = "Unexpected arguments: " + ' '.join(command[1:])
    elif len(command) < 3:
        me = "Too few arguments."
    elif len(command) > 3:
        me = "Too many arguments."
    elif not vm_const(command[2]):
        me = "Except a constant not: " + command[2]
    return C_ERROR if me else FUNC_INST[command[0]], me

"""The CodeWriter module provide 

  * set_file_name, write_arithmetic and write_push_pop (Project 07)
  * write_label, write_goto, write_if, write_call, write_function, 
    write_return (Project 08)

for translating vm command into asm language and write it into a new file.
"""

import os
from vm_definitions import *

class CodeWriter:
    def __init__(self, out_path):
        self._file = open(out_path, 'w')
        self._vm_name = None
        self._next_end_label = 0
        self._next_ret_label = 0

    def set_file_name(self, filename):
        self._vm_name, _ = os.path.splitext(filename)

    def write_sys_init(self):
        self._assign(256, 'D', 'A')                 # D = 256
        self._assign('SP', 'M', 'D')                # SP = 256
        self.write_call('Sys.init', 0)              # call Sys.init

    def write_push_pop(self, command, seg, index):
        if command == C_PUSH:
            self.write_push(seg, index)
        elif command == C_POP:
            self.write_pop(seg, index)

    def write_arithmetic(self, command):
        """'add', 'sub', 'neg', 'eq' , 'gt', 'lt', 'and', 'or', 'not'"""
        return (self._binary_arith('D+M')  if command == 'add' else
                self._binary_arith('M-D')  if command == 'sub' else
                self._binary_arith('D&M')  if command == 'and' else
                self._binary_arith('D|M')  if command == 'or'  else
                self._unary_arith('-M')    if command == 'neg' else
                self._unary_arith('!M')    if command == 'not' else
                self._compare_arith('JEQ') if command == 'eq'  else
                self._compare_arith('JGT') if command == 'gt'  else
                self._compare_arith('JLT') if command == 'lt'  else None)

    def write_label(self, label):
        self.write_l_command(label)                 # (label)

    def write_goto(self, label):
        self._jump(label, '0', 'JMP')               # A=&label, 0;JMP

    def write_if(self, label):
        self._pop_from_stack('D')                   # SP--, D=*SP
        self._jump(label, 'D', 'JNE')               # A=&label, D;JNE

    def write_call(self, func_name, num_args):
        return_label = self._new_ret_label()
        self.write_push(S_CONST, return_label)      # push return address
        self._save_pointer(R_LCL)                   # push LCL
        self._save_pointer(R_ARG)                   # push ARG
        self._save_pointer(R_THIS)                  # push THIS
        self._save_pointer(R_THAT)                  # push THAT
        self._reg_transfer('ARG', 'SP', offset=-int(num_args)-5)
                                                    # ARG = SP-n-5
        self._reg_transfer('LCL', 'SP')             # LCL = SP
        self.write_goto(func_name)                  # goto f
        self.write_l_command(return_label)          # (return_label)

    def write_return(self):
        self._reg_transfer(R_FRAME, 'LCL')          # FRAME = LCL
        self._restore_pointer(R_RET, -5)            # RET = *(FRAME-5)
        self.write_pop(S_ARG, '0')                  # *ARG = return value
        self._reg_transfer('SP', 'ARG', offset=1)   # SP = ARG+1
        self._restore_pointer('THAT', -1)           # THAT = *(FRAME-1)
        self._restore_pointer('THIS', -2)           # THIS = *(FRAME-2)
        self._restore_pointer('ARG', -3)            # ARG = *(FRAME-3)
        self._restore_pointer('LCL', -4)            # LCL = *(FRAME-4)
        self._assign(R_RET, 'A', 'M')               # A = R_RET
        self.write_c_command('0', jump='JMP')       # goto RET

    def write_function(self, func_name, num_locals):
        self.write_l_command(func_name)
        for _ in range(int(num_locals)):
            self.write_push(S_CONST, '0')

    def close(self):
        self._file.close()

    ##################################
    # Code write function for output #
    ##################################

    def write(self, text):
        self._file.write(text)

    def write_a_command(self, addr_or_sym):
        """addr_or_sym: int or string"""
        self.write("@%s\n" %addr_or_sym)

    def write_l_command(self, symbol):
        self.write("(%s)\n" %symbol)

    def write_c_command(self, comp, dest='', jump=''):
        if dest:
            dest = dest + '='
        if jump:
            jump = ';' + jump
        self.write(dest + comp + jump + '\n')

    def _assign(self, addr_or_sym, dest, comp):
        self.write_a_command(addr_or_sym)           # A = &addr_or_sym
        self.write_c_command(comp, dest=dest)       # dest = comp

    def _jump(self, label, comp, jump):
        self.write_a_command(label)                 # A = &label
        self.write_c_command(comp, jump=jump)       # comp;jump

    ####################
    # stack operations #
    ####################

    # stack pointer operations
    def _write_sp(self, comp):
        self._assign('SP', 'A', 'M')                # A = SP
        self.write_c_command(comp, dest='M')        # *SP = comp

    def _load_sp_val(self, dest):
        """return the value of the address that the stack pointer point to
        in the memory."""
        self._assign('SP', 'A', 'M')                # A = SP
        self.write_c_command('M', dest=dest)        # dest = *SP

    def _push_to_stack(self, comp):
        self._write_sp(comp)                        # *SP = comp
        self._assign('SP', 'M', 'M+1')              # SP++

    def _pop_from_stack(self, dest):
        self._assign('SP', 'AM', 'M-1')             # SP--, A=SP
        self.write_c_command('M', dest=dest)        # dest = *SP

    # stack operations
    def write_push(self, seg, index):
        comp = 'A' if seg == S_CONST else 'M'
        self._get_seg_address(seg, index)           # A = index or target_address
        self.write_c_command(comp, dest='D')        # D = const or *addr
        self._push_to_stack('D')                    # *SP=D, SP++

    def write_pop(self, seg, index):
        if is_memo_seg(seg):
            self._assign('SP', 'M', 'M-1')          # SP--
            self._get_memo_address(seg, index)      # A = seg+index
            self.write_c_command('A', dest='D')     # D = A
            self._assign(R_COPY, 'M', 'D')          # R_COPY = D
            self._load_sp_val('D')                  # D = *SP
            self._assign(R_COPY, 'A', 'M')          # A = R_CORY
        else:
            self._pop_from_stack('D')               # SP--, D=*SP
            self._get_seg_address(seg, index)       # A = target_address
        self.write_c_command('D', dest='M')         # *addr = *SP

    # for getting SEGMENT address with or without offset
    def _get_seg_address(self, seg, index):
        return (self._get_memo_address(seg, index) if is_memo_seg(seg)   else
                self._get_reg_address(seg, index)  if is_reg_seg(seg)    else
                self._get_static_address(index)    if is_static_seg(seg) else
                self._get_const(index)             if is_const_seg(seg)  else None)

    def _get_memo_address(self, seg, index):
        self._assign(MEMO_SYMBOLS[seg], 'A', 'M')   # A = seg
        if index != '0':
            self.write_c_command('A', dest='D')     # D = seg
            self._assign(index, 'A', 'D+A')         # A = seg+index

    def _get_reg_address(self, seg, index):
        sym = 'R' + str(REG_ADDRESS[seg] + int(index))
        self.write_a_command(sym)                   # A = &seg+index

    def _get_static_address(self, index):
        static_name = '.'.join((self._vm_name, index))
        self.write_a_command(static_name)

    def _get_const(self, const):
        self.write_a_command(const)                 # A = const

    #########################
    # arithmetic operations #
    #########################

    def _binary_arith(self, comp):
        self._pop_from_stack('D')                   # SP--, A=SP, D=*SP
        self.write_c_command('A-1', dest='A')       # A = SP-1
        self.write_c_command(comp, dest='M')        # *(SP-1) = comp

    def _unary_arith(self, comp):
        self._assign('SP', 'A', 'M-1')              # A = SP-1
        self.write_c_command(comp, dest='M')        # D = *(SP-1)

    def _compare_arith(self, jump):
        label = self._new_end_label()
        self._pop_from_stack('D')                   # SP--, A=SP, D=*SP
        self.write_c_command('A-1', dest='A')       # A = SP-1
        self.write_c_command('M-D', dest='D')       # D = *(SP-1) - *SP
        # assume the test pass
        self.write_c_command('-1', dest='M')        # *(SP-1) = true
        self._jump(label, 'D', jump)                # D;jump
        # if test haven't pass, then change the *(SP-1)
        self._assign('SP', 'A', 'M-1')              # A = SP-1
        self.write_c_command('0', dest='M')         # *(SP-1) = 0
        self.write_l_command(label)                 # (label)

    def _new_end_label(self):
        self._next_end_label += 1
        return 'END_' + str(self._next_end_label)

    def _new_ret_label(self):
        self._next_ret_label += 1
        return 'RETURN_' + str(self._next_ret_label)

    ###############################
    # function calling operations #
    ###############################

    def _load_reg_val(self, addr_or_sym, dest='A', offset=0):
        """return the address stored in register (with a specific symbol) with
        or without offset"""
        if offset == 0:
            self._assign(addr_or_sym, dest, 'M')        # dest = symbol
        else:
            comp = 'D+M' if offset > 0 else 'M-D'
            self._assign(abs(offset), 'D', 'A')         # D = abs(offset)
            self._assign(addr_or_sym, dest, comp)       # dest = symbol+/-D

    def _reg_transfer(self, to, fr, offset=0):
        self._load_reg_val(fr, dest='D', offset=offset) # D = fr+offset
        self._assign(to, 'M', 'D')                      # to = D

    def _save_pointer(self, address):
        self._assign(address, 'D', 'M')                 # D = *address
        self._push_to_stack('D')                        # *SP = D, SP++

    def _restore_pointer(self, addr_or_sym, offset):
        """restore pointer value from FRAME with offset"""
        self._load_reg_val(R_FRAME, offset=offset)      # A = frame+offset
        self.write_c_command('M', dest='D')             # D = *A
        self._assign(addr_or_sym, 'M', 'D')             # *addr_or_sym = D

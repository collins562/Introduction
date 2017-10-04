"""The vm_translator module provides translate function to translate vm language
to asm language in another file."""

import os
from Parser import Parser
from CodeWriter import CodeWriter
from vm_definitions import *

def is_vm_file(filename):
    return filename.endswith('.vm')

def retrive_files(path):
    has_sys_init = False
    filepaths = []
    dirpath, ext = os.path.splitext(path)
    if ext != '':
        if ext != '.vm':
            raise ValueError("Except a vm file.")
        filepaths.append(path)
        outpath = dirpath + '.asm'
    else:
        outpath = os.path.join(path, os.path.basename(path) + '.asm')
        filenames = filter(is_vm_file, os.listdir(path))
        for name in filenames:
            filepaths.append(os.path.join(path, name))
            if name == 'Sys.vm':
                has_sys_init = True
    return has_sys_init, filepaths, outpath

def translate(path):
    """translate vm language in a vm file or files in the path to asm language
    in other files.
        path: dirpath or filepath
    """
    has_sys_init, filepaths, outpath = retrive_files(path)
    writer = CodeWriter(outpath)
    if has_sys_init:
        writer.write_sys_init()
    for filepath in filepaths:
        filename = os.path.basename(filepath)
        writer.set_file_name(filename)
        parser = Parser(filepath)
        translate_file(parser, writer)
    writer.close()

def translate_file(parser, writer):
    """translate vm language in a file to asm language in another file:
        parser: object that store parsed vm commands from a file
        writer: object that translate vm commands and write it into a file
    """    
    while parser.has_more_commands():
        parser.advance()
        command = parser.command_type
        if command == C_ARITHMETIC:
            writer.write_arithmetic(parser.arg1)
        elif command == C_PUSH or command == C_POP:
            writer.write_push_pop(command, parser.arg1, parser.arg2)
        elif command == C_LABEL:
            writer.write_label(parser.arg1)
        elif command == C_GOTO:
            writer.write_goto(parser.arg1)
        elif command == C_IF:
            writer.write_if(parser.arg1)
        elif command == C_FUNCTION:
            writer.write_function(parser.arg1, parser.arg2)
        elif command == C_RETURN:
            writer.write_return()
        elif command == C_CALL:
            writer.write_call(parser.arg1, parser.arg2)

def main():
    translate('ProgramFlow\\BasicLoop')
    translate('ProgramFlow\\FibonacciSeries')
    translate('FunctionCalls\\FibonacciElement')
    translate('FunctionCalls\\NestedCall')
    translate('FunctionCalls\\SimpleFunction')
    translate('FunctionCalls\\StaticsTest')

if __name__ == '__main__':
    main()
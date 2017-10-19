"""The JackCompiler module provides class JackCompiler for compiling Jack language
in a jack file to vm language in another file.
"""

import os, sys
from JackTokenizer import Tokenizer
from JackDefinitions import *
from CompilationEngine import CompilationEngine

def is_jack_file(filename):
    return filename.endswith('.jack')

class JackCompiler:
    def retrieve_files(self, path):
        dirpath, ext = os.path.splitext(path)
        if ext != '':
            if ext != '.jack':
                raise ValueError("Expect a jack file.")
            return [path]
        else:
            filenames = filter(is_jack_file, os.listdir(path))
            return (os.path.join(path, name) for name in filenames)

    def compile(self, inpath, outpath=None):
        if not os.path.exists(inpath):
            raise FileNotFoundError('module not found.')
        res_path = inpath if outpath is None else outpath
        infiles = self.retrieve_files(inpath)
        for infile in infiles:
            outfile = os.path.basename(infile).replace('.jack', '.vm')
            outpath = os.path.join(res_path, outfile)
            CompilationEngine(infile, outpath)

def test():
    compiler = JackCompiler()
    compiler.compile('Seven')
    compiler.compile('ConvertToBin')
    compiler.compile('Square')
    compiler.compile('Average')
    compiler.compile('Pong')
    compiler.compile('ComplexArrays')

def main():
    if len(sys.argv) != 2:
        print("Usage: JackCompiler dirpath")
    else:
        compiler = JackCompiler()
        compiler.compiler(sys.argv[1])

# main()
test()

"""The JackCompiler module provides class JackCompiler for compiling Jack language
in a jack file to vm language in another file.
"""

import os, sys
from JackTokenizer import Tokenizer
from JackDefinitions import *
from CompilationEngine import CompilationEngine

RES_PATH = 'compiled'
OS_PATH = 'OS'

def is_jack_file(filename):
    return filename.endswith('.jack')

class JackCompiler:
    def retrieve_files(self, path):
        dirpath, ext = os.path.splitext(path)
        self.set_up_outpath(dirpath)
        if ext != '':
            if ext != '.jack':
                raise ValueError("Expect a jack file.")
            return [path]
        else:
            filenames = filter(is_jack_file, os.listdir(path))
            return (os.path.join(path, name) for name in filenames)

    def set_up_outpath(self, dirpath):
        self.out_dirpath = os.path.join(dirpath, RES_PATH)
        if not os.path.exists(self.out_dirpath):
            os.mkdir(self.out_dirpath)
        for osfile in os.listdir(OS_PATH):
            self.copy(osfile)

    def copy(self, osfile):
        with open(os.path.join(OS_PATH, osfile), 'r') as f:
            text = f.read()
        with open(os.path.join(self.out_dirpath, osfile), 'w') as f:
            f.write(text)

    def compile(self, inpath):
        infiles = self.retrieve_files(inpath)
        for infile in infiles:
            outfile = os.path.basename(infile).replace('.jack', '.vm')
            outpath = os.path.join(self.out_dirpath, outfile)
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
        print("Usage: JackCompiler [filename.jack | dirpath]")
    else:
        Jack_to_xml(sys.argv[1])

# main()
test()

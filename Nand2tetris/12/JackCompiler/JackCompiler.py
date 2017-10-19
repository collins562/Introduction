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
    def __init__(self):
        root_path = os.path.split(sys.path[0])[0]
        self.imple_path = os.path.join(root_path, 'OSImplementation')
        self.test_path = os.path.join(root_path, 'Test')
        self.res_path = None

    def retrieve_files(self, path):
        dirpath, ext = os.path.splitext(path)
        if ext != '':
            if ext != '.jack':
                raise ValueError("Expect a jack file.")
            return [path]
        else:
            filenames = filter(is_jack_file, os.listdir(path))
            return (os.path.join(path, name) for name in filenames)

    def copy(self, src):
        with open(os.path.join(src), 'r') as f:
            text = f.read()
        with open(os.path.join(self.res_path, os.path.basename(src)), 'w') as f:
            f.write(text)

    def compile(self, inpath):
        infiles = self.retrieve_files(inpath)
        for infile in infiles:
            outfile = os.path.basename(infile).replace('.jack', '.vm')
            outpath = os.path.join(self.res_path, outfile)
            CompilationEngine(infile, outpath)

def compile_implementation(module):
    compiler = JackCompiler()
    compiler.res_path = os.path.join(compiler.test_path, module + 'Test')
    imple_file = module + '.jack'
    filepath = os.path.join(compiler.imple_path, imple_file)
    if not os.path.exists(filepath):
        raise FileNotFoundError('module not found.')
    compiler.copy(filepath)
    compiler.compile(compiler.res_path)

def test():
    compile_implementation('Math')
    compile_implementation('String')
    compile_implementation('Array')
    compile_implementation('Output')
    compile_implementation('Screen')
    compile_implementation('Keyboard')
    compile_implementation('Memory')
    compile_implementation('Sys')

def main():
    if len(sys.argv) != 2:
        print("Usage: JackCompiler dirpath")
    else:
        compile_implementation(sys.argv[1])

# main()
test()

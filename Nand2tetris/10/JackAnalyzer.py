"""The JackAnalyzer module provides class TokenAnalyzer and JackAnalyzer, and
functions tokens_to_xml and Jack_to_xml for converting the structure of a jack
file text to xml structure.
"""

import os, sys
from JackTokenizer import Tokenizer
from JackDefinitions import *
from Compiler import Compiler

def is_jack_file(filename):
    return filename.endswith('.jack')

def retrive_files(path):
    dirpath, ext = os.path.splitext(path)
    if ext != '':
        if ext != '.jack':
            raise ValueError("Expect a jack file.")
        return [path]
    else:
        filenames = filter(is_jack_file, os.listdir(path))
        return [os.path.join(path, name) for name in filenames]

class TokenAnalyzer:
    """A simple analyzer for writing tag info of non-compiled tokens into
    a xml file."""
    def __init__(self, outpath):
        self._file = open(outpath, 'w')
        self.write('<tokens>\n')

    text_convert = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}

    def write(self, text):
        self._file.write(text)

    def write_info(self, text, tag):
        try:
            text = self.text_convert[text]
        except KeyError:
            pass
        self.write('<' + tag + '>')
        self.write(' ' + str(text) + ' ')
        self.write('</' + tag + '>\n')

    def close(self):
        self.write('</tokens>\n')
        self._file.close()

def tokens_to_xml(path):
    """Write the tokens into a xml file with its type as tags. The outpath
    is the dirpath of the a new directory in the module path to avoid name
    clashes."""
    paths = retrive_files(path)
    out_dirpath = os.path.join(path, 'Xmlresult')
    for path in paths:
        outfile = os.path.basename(path).replace('.jack', 'T.xml')
        outpath = os.path.join(out_dirpath, outfile)
        tokenizer = Tokenizer(path)
        analyzer = TokenAnalyzer(outpath)
        while tokenizer.has_more_tokens():
            tokenizer.advance()
            t_type = tokenizer.token_type
            tag = token_tags[t_type]
            if t_type == T_KEYWORD:
                analyzer.write_info(tokenizer.keyword, tag)
            elif t_type == T_SYMBOL:
                analyzer.write_info(tokenizer.symbol, tag)
            elif t_type == T_ID:
                analyzer.write_info(tokenizer.identifier, tag)
            elif t_type == T_INTEGER:
                analyzer.write_info(tokenizer.intval, tag)
            elif t_type == T_STRING:
                analyzer.write_info(tokenizer.stringval, tag)
        analyzer.close()

def Jack_to_xml(path):
    paths = retrive_files(path)
    out_dirpath = os.path.join(path, 'Xmlresult')
    for path in paths:
        outfile = os.path.basename(path).replace('.jack', '.xml')
        outpath = os.path.join(out_dirpath, outfile)
        compiler = Compiler(path, outpath)

def test():
    tokens_to_xml('ArrayTest')
    tokens_to_xml('ExpressionLessSquare')
    tokens_to_xml('Square')
    Jack_to_xml('ArrayTest')
    Jack_to_xml('ExpressionLessSquare')
    Jack_to_xml('Square')

def main():
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer [filename.jack | dirpath]")
    else:
        Jack_to_xml(sys.argv[1])

test()

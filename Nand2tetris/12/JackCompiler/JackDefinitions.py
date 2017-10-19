"""The JackDefinitions module provides type define of tokens, keywords
and symbols, and check functions for the tokens in the jack files. 
"""

# Token types
T_KEYWORD       = 0     # keyword e.g. 'class', 'false' etc
T_SYMBOL        = 1     # symbol e.g. '{', '}' etc
T_INTEGER       = 2     # integer e.g. '123' - from 0 to 32767
T_STRING        = 3     # string e.g. "Hello, World."
T_ID            = 4     # identifier e.g. 'name', 'id_42'
T_ERROR         = 5     # error in file

# Keywords for token type T_KEYWORD
KW_CLASS        = 'class'
KW_METHOD       = 'method'
KW_FUNCTION     = 'function'
KW_CONSTRUCTOR  = 'constructor'
KW_INT          = 'int'
KW_BOOLEAN      = 'boolean'
KW_CHAR         = 'char'
KW_VOID         = 'void'
KW_VAR          = 'var'
KW_STATIC       = 'static'
KW_FIELD        = 'field'
KW_LET          = 'let'
KW_DO           = 'do'
KW_IF           = 'if'
KW_ELSE         = 'else'
KW_WHILE        = 'while'
KW_RETURN       = 'return'
KW_TRUE         = 'true'
KW_FALSE        = 'false'
KW_NULL         = 'null'
KW_THIS         = 'this'

keywords = (KW_CLASS, KW_METHOD, KW_FUNCTION, KW_CONSTRUCTOR, KW_INT,
            KW_BOOLEAN, KW_CHAR, KW_VOID, KW_VAR, KW_STATIC, KW_FIELD, 
            KW_LET, KW_DO, KW_IF, KW_ELSE, KW_WHILE, KW_RETURN, KW_TRUE, 
            KW_FALSE, KW_NULL, KW_THIS)

ops = ('+', '-', '*', '/', '&', '|', '~', '<', '>', '=', '-')

symbols = ('{', '}', '(', ')', '[', ']', '.', ',', ';') + ops

# Tokens for sample output
token_tags = ['keyword', 'symbol', 'integerConstant', 'stringConstant', 
              'identifier']

def is_keyword(s):
    return s in keywords

def is_symbol(s):
    return s in symbols

def is_op(s):
    return s in ops

def is_integer(s):
    return type(s) == int or s.isdigit()

def is_string(s):
    return s.startswith('"')

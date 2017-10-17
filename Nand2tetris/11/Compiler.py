"""The Compiler module provides class Compiler to compile text in Jack language
into vm language and write it into a vmfile. Jack language has structures:

  * class
  * classVarDec
  * subroutine
  * parameterList
  * varDec
  * statements (doStatement, letStatement, whileStatement, returnStatement,
                ifStatement)
  * expression
  * expressionList
  * term

"""

import os
from JackTokenizer import Tokenizer
from JackDefinitions import *
from SymbolTable import *

STACK = []

def record_non_terminal(non_terminal):
    def compile_fn(procedure):
        def fn(instance):
            STACK.append(non_terminal)
            procedure(instance)
            STACK.pop()
        return fn
    return compile_fn

class CompileError(Exception):
    pass

class Compiler:
    def __init__(self, inpath, outpath):
        self.tokenizer = Tokenizer(inpath)
        self.symboltable = SymbolTable()
        self.vmwriter = VMWriter()
        self.class_name = None
        if self.tokenizer.has_more_tokens():
            self.compile_class()
        self.vmwriter.close()
        print("{0} completed.".format(os.path.basename(inpath)))

    token_convert = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}
    type_kws = (KW_INT, KW_CHAR, KW_BOOLEAN)
    kw_consts = (KW_TRUE, KW_FALSE, KW_NULL, KW_THIS)

    def write(self, text):
        self._file.write(text)

    def write_tag(self, tag, end=False, newline=False):
        head = '</' if end else '<'
        tail = '>\n' if newline else '>'
        self.write(head + tag + tail)

    def write_terminal(self, terminal, tok_tag):
        if terminal in self.token_convert:
            terminal = self.token_convert[terminal]
        self.write_tag(tok_tag)
        self.write(' ' + str(terminal) + ' ')
        self.write_tag(tok_tag, end=True, newline=True)

    def write_non_terminal(self, non_terminal, end=False):
        self.write_tag(non_terminal, end=end, newline=True)

    def _write_current_terminal(self):
        self.write_terminal(self._current_token, self._current_tok_tag)

    def _advance(self):
        self._check_EOF()
        self.tokenizer.advance()

    @property
    def _current_token(self):
        t_type = self.tokenizer.token_type
        return (self.tokenizer.keyword    if t_type == T_KEYWORD else
                self.tokenizer.symbol     if t_type == T_SYMBOL  else
                self.tokenizer.identifier if t_type == T_ID      else
                self.tokenizer.intval     if t_type == T_INTEGER else
                self.tokenizer.stringval)

    @property
    def _current_tok_type(self):
        return self.tokenizer.token_type

    @property
    def _current_tok_tag(self):
        return token_tags[self._current_tok_type]

    @property
    def _next_token(self):
        """return raw next_token in the tokenizer"""
        return str(self.tokenizer.next_token)

    def _require_token(self, tok_type, token=None, write=True):
        """Check whether the next_token(terminal) in the tokenizer meets the 
        requirement (specific token or just token type). If meets, tokenizer
        advances (update current_token and next_token)  and terminal will be 
        writed into outfile; If not, report an error."""
        self._advance()
        if token and self._current_token != token:
            me = 'Expect "{0}" but get "{1}"'.format(token, self._current_token)
            self._traceback(me)
        elif self._current_tok_type != tok_type:
            require_tag = token_tags[tok_type]
            tok = self._current_token
            me = 'Expect type {0} but get "{1}"'.format(require_tag, tok)
            self._traceback(me)
        if write is True:
            self._write_current_terminal()

    def _require_id(self, kind=None, type=None, declare=False):
        self._require_token(T_ID, write=False)
        name = self._current_token
        defined = False
        used = False
        if declare is True:     # kind is not None
            self.symboltable.define(name, type, kind)
            index = self.symboltable.indexof(name)
            defined = True
        else:
            if kind is None:
                kind = self.symboltable.kindof(name)
            if is_class_kind(kind) or is_subroutine_kind(kind):
                index = self.symboltable.indexof(name)
            else:
                index = None
        info = '(kind:{0} defined:{1} used:{2} index:{3})'.format(kind, defined, used, index)
        self.write_terminal('{0}: {1}'.format(name, info), self._current_tok_tag)

    def _require_kw(self, token):
        return self._require_token(T_KEYWORD, token=token)

    def _require_sym(self, token):
        return self._require_token(T_SYMBOL, token=token)

    def _optional_nonstrs(self, tokens, tok_types=(), expect=None, advanced=False):
        """Check whether the non-string next_token(terminal) in tokenizer meets
        one of requirement (tokens or tok_types).  If meets, tokenizer advances
        (update current_token and next_token)  and terminal will be writed into
        outfile; If not, report an error. tokens, tok_types: tuple; expect: for
        error report"""
        if advanced is False:
            self._advance()
        if self._current_tok_type != T_STRING:
            for token in tokens:
                if token == self._current_token:
                    return self.write_terminal(token, self._current_tok_tag)
            for t_type in tok_types:
                if t_type == self._current_tok_type:
                    return self._write_current_terminal()
        # current token is not eligible, report an error
        if expect is None:
            expect_toks = ' or '.join(('"{0}"'.format(t) for t in tokens))
            expect_types = ' or '.join(('type ' + token_tags[t] for t in tok_types))
            expect = ' or '.join([expect_toks, expect_types])
        me = 'Expect {0} but get "{1}"'.format(expect, self._current_token)
        self._traceback(me)

    def _followed_by(self, tokens):
        """Check if current_token is followed by one of the input tokens 
        (iterable)."""
        return any(self._next_token == tok for tok in tokens)

    def _fol_by_class_vardec(self):
        return self._followed_by((KW_STATIC, KW_FIELD))

    def _fol_by_subroutine(self):
        return self._followed_by((KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD))

    def _fol_by_vardec(self):
        return self._followed_by((KW_VAR,))

    def compile_non_terminal(self, non_terminal, compile_procedure):
        # <non_terminal> compile_procedure() </non_terminal>
        self.write_non_terminal(non_terminal)
        compile_procedure()
        self.write_non_terminal(non_terminal, end=True)

    #########################
    # structure compilation #
    #########################

    def compile_type(self):
        self._optional_nonstrs(self.type_kws, (T_ID,), 'type')

    def compile_void_or_type(self):
        self._optional_nonstrs((KW_VOID,) + self.type_kws, (T_ID,), '"void" or type')

    @record_non_terminal('class')
    def compile_class(self):
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self._require_kw(KW_CLASS)
        self._require_id('class')
        self.class_name = self._current_token
        self._require_sym('{')
        while self._fol_by_class_vardec():
            self.compile_class_vardec()
        while self._fol_by_subroutine():
            self.compile_subroutine(class_name)
        self._advance()
        if self._current_token != '}':
            self._traceback("Except classVarDec or subroutineDec.")
        self._write_current_terminal()

    def compile_declare(self):
        self._advance()
        id_kind = self._current_token       # ('static | field | var')
        # type varName (',' varName)* ';'
        self.compile_type()
        id_type = self._current_token
        self._require_id(id_kind, id_type, True)
        self._optional_nonstrs((',', ';'))
        while self._current_token == ',':
            self._require_id(id_kind, id_type, True)
            self._optional_nonstrs((',', ';'))

    def compile_class_vardec(self):
        # ('static|field') type varName (',' varName)* ';'
        self.compile_declare()

    @record_non_terminal('subroutineDec')
    def compile_subroutine(self):
        # ('constructor'|'function'|'method')
        # ('void'|type) subroutineName '(' parameterList ')' subroutineBody
        self.symboltable.start_subroutine()
        self._advance()
        self._write_current_terminal()      # ('constructor'|'function'|'method')
        self.compile_void_or_type()
        self._require_id('subroutine')
        self._require_sym('(')
        self.compile_non_terminal('parameterList', self.compile_parameter_list)
        self._require_sym(')')
        self.compile_non_terminal('subroutineBody', self.compile_subroutine_body)

    def compile_parameter_list(self):
        # ((type varName) (',' type varName)*)?
        if self._next_token == ')':
            return
        self.compile_type()
        self._require_id('argument', self._current_token, True)
        while self._next_token != ')':
            self._require_sym(',')
            self.compile_type()
            self._require_id('argument', self._current_token, True)

    def compile_subroutine_body(self):
        # '{' varDec* statements '}'
        self._require_sym('{')
        while self._fol_by_vardec():
            self.compile_non_terminal('varDec', self.compile_vardec)
        self.compile_non_terminal('statements', self.compile_statements)
        self._require_sym('}')

    def compile_vardec(self):
        # 'var' type varName (',' varName)* ';'
        self.compile_declare()

    #########################
    # statement compilation #
    #########################

    def compile_statements(self):
        # (letStatement | ifStatement | whileStatement | doStatement | 
        # returnStatement)*
        while self._next_token != '}':
            self._advance()
            tok = self._current_token
            if tok == 'do':
                self.compile_non_terminal('doStatement', self.compile_do)
            elif tok == 'let':
                self.compile_non_terminal('letStatement', self.compile_let)
            elif tok == 'while':
                self.compile_non_terminal('whileStatement', self.compile_while)
            elif tok == 'return':
                self.compile_non_terminal('returnStatement', self.compile_return)
            elif tok == 'if':
                self.compile_non_terminal('ifStatement', self.compile_if)
            else:
                me = 'Expect statement expression but get "{0}"'.format(tok)
                self._traceback(me)

    def compile_do(self):
        # 'do' subroutineCall ';'
        self._write_current_terminal()
        # compile identifier first
        self._require_token(T_ID)
        self.compile_subroutine_call()
        self._require_sym(';')

    def compile_let(self):
        # 'let' varName ('[' expression ']')? '=' expression ';'
        self._write_current_terminal()
        self._require_token(T_ID)
        if self._next_token != '=':
            self._require_sym('[')
            self.compile_non_terminal('expression', self.compile_expression)
            self._require_sym(']')
        self._require_sym('=')
        self.compile_non_terminal('expression', self.compile_expression)
        self._require_sym(';')

    def compile_while(self):
        # 'while' '(' expression ')' '{' statements '}'
        self._write_current_terminal()
        self._require_sym('(')
        self.compile_non_terminal('expression', self.compile_expression)
        self._require_sym(')')
        self._require_sym('{')
        self.compile_non_terminal('statements', self.compile_statements)
        self._require_sym('}')

    def compile_return(self):
        # 'return' expression? ';'
        self._write_current_terminal()
        if self._next_token != ';':
            self.compile_non_terminal('expression', self.compile_expression)
        self._require_sym(';')

    def compile_if(self):
        # 'if' '(' expression ')' '{' statements '}'
        # ('else' '{' statements '}')?
        self._write_current_terminal()
        self._require_sym('(')
        self.compile_non_terminal('expression', self.compile_expression)
        self._require_sym(')')
        self._require_sym('{')
        self.compile_non_terminal('statements', self.compile_statements)
        self._require_sym('}')
        # else clause
        if self._next_token == KW_ELSE:
            self._require_kw(KW_ELSE)
            self._require_sym('{')
            self.compile_non_terminal('statements', self.compile_statements)
            self._require_sym('}')

    ##########################
    # expression compilation #
    ##########################

    def compile_expression(self):
        # term (op term)*
        self.compile_non_terminal('term', self.compile_term)
        while is_op(self._next_token):
            self.compile_op()
            self.compile_non_terminal('term', self.compile_term)

    def compile_term(self):
        # integerConstant | stringConstant | keywordConstant |
        # varName | varName '[' expression ']' | subroutineCall |
        # '(' expression ')' | unaryOp term
        if self._next_token == '(':
            self._require_sym('(')
            self.compile_non_terminal('expression', self.compile_expression)
            self._require_sym(')')
        elif self._next_token in set('-~'):
            self.compile_unaryop()
        else:
            self._advance()
            tok = self._current_token
            tok_type = self._current_tok_type
            if tok_type == T_ID:
                self._write_current_terminal()
                if self._next_token == '[':
                    self._compile_array_subscript()
                elif self._next_token in '(.':
                    self.compile_subroutine_call()
            elif tok_type == T_STRING:
                self._write_current_terminal()
            else:
                self._optional_nonstrs(self.kw_consts, (T_INTEGER,), 'term', True)

    def compile_subroutine_call(self):
        # subroutineName '(' expressionList ')' | (className |
        # varName) '.' subroutineName '(' expressionList ')'
        ## the first element of structure has already been compiled.
        if self._next_token == '.':
            self._require_sym('.')
            self._require_token(T_ID)
        self._require_sym('(')
        self.compile_non_terminal('expressionList', self.compile_expressionlist)
        self._require_sym(')')

    def compile_expressionlist(self):
        # (expression (',' expression)*)?
        if self._next_token != ')':
            self.compile_non_terminal('expression', self.compile_expression)
        while self._next_token != ')':
            self._require_sym(',')
            self.compile_non_terminal('expression', self.compile_expression)

    def compile_op(self):
        # exclude '~'
        self._advance()
        if self._current_token == '~':
            self._traceback('Unexpected operator: ~')
        self._write_current_terminal()

    def compile_unaryop(self):
        self._advance()
        self._write_current_terminal()      # symbol: - or ~
        self.compile_non_terminal('term', self.compile_term)

    def _compile_array_subscript(self):
        # '[' expression ']'
        self._require_sym('[')
        self.compile_non_terminal('expression', self.compile_expression)
        self._require_sym(']')

    def _check_EOF(self):
        if not self.tokenizer.has_more_tokens():
            self._traceback("Unexpected EOF.")

    def _traceback(self, message):
        file_info = 'file: "{0}"'.format(self.tokenizer.filename)
        line_info = 'line {0}'.format(self.tokenizer.line_count)
        raise CompileError("{0}, {1}: {2}".format(file_info, line_info, message))
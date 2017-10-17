"""The Compiler module provides class Compiler to compile text in Jack language
into xml structure and write it into a xmlfile. Jack language has structures:

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

from JackTokenizer import Tokenizer
from JackDefinitions import *
from XMLWriter import XMLWriter

STACK = []
XMLWriter = XMLWriter()

def record_non_terminal(non_terminal):
    def fn(procedure):
        def compile_fn(instance):
            STACK.append(non_terminal)
            XMLWriter.write_non_terminal(non_terminal)
            procedure(instance)
            XMLWriter.write_non_terminal(STACK.pop(), True)            
        return compile_fn
    return fn

class CompileError(Exception):
    pass

class Compiler:
    def __init__(self, inpath, outpath):
        self.tokenizer = Tokenizer(inpath)
        XMLWriter.set_filepath(outpath)
        if self.tokenizer.has_more_tokens():
            self.compile_class()
        XMLWriter.close()

    def _write_current_terminal(self):
        XMLWriter.write_terminal(self._current_token, self._current_tok_tag)

    def _advance(self):
        self._check_EOF()
        self.tokenizer.advance()

    type_kws = (KW_INT, KW_CHAR, KW_BOOLEAN)
    kw_consts = (KW_TRUE, KW_FALSE, KW_NULL, KW_THIS)

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

    def _require_token(self, tok_type, token=None):
        """Check whether the next_token(terminal) in the tokenizer meets the 
        requirement (specific token or just token type). If meets, tokenizer
        advances (update current_token and next_token)  and terminal will be 
        writed into outfile; If not, report an error."""
        self._advance()
        if token and self._current_token != token:
            return self._error(expect_toks=(token,))
        elif self._current_tok_type != tok_type:
            return self._error(expect_types=(tok_type,))
        self._write_current_terminal()

    def _require_id(self):
        return self._require_token(T_ID)

    def _require_kw(self, token):
        return self._require_token(T_KEYWORD, token=token)

    def _require_sym(self, token):
        return self._require_token(T_SYMBOL, token=token)

    def _require_brackets(self, brackets, procedure):
        front, back = brackets
        self._require_sym(front)
        procedure()
        self._require_sym(back)

    def _fol_by_class_vardec(self):
        return self._next_token in (KW_STATIC, KW_FIELD)

    def _fol_by_subroutine(self):
        return self._next_token in (KW_CONSTRUCTOR, KW_FUNCTION, KW_METHOD)

    def _fol_by_vardec(self):
        return self._next_token == KW_VAR

    #########################
    # structure compilation #
    #########################

    # the compilation of three types of name might seem redundant here, but
    # it was for abstraction and later code generation in project 11.
    def compile_class_name(self):
        self._require_id()

    def compile_subroutine_name(self):
        self._require_id()

    def compile_var_name(self):
        self._require_id()

    def compile_type(self, advanced=False, expect='type'):
        # int, string, boolean or identifier(className)
        if advanced is False:
            self._advance()
        if self._current_token in self.type_kws:
            return self._write_current_terminal()
        elif self._current_tok_type == T_ID:
            return self._write_current_terminal()
        else:
            return self._error(expect=expect)

    def compile_void_or_type(self):
        # void or type
        self._advance()
        if self._current_token == KW_VOID:
            self._write_current_terminal()
        else:
            self.compile_type(True, '"void" or type')

    @record_non_terminal('class')
    def compile_class(self):
        # 'class' className '{' classVarDec* subroutineDec* '}'
        self._require_kw(KW_CLASS)
        self.compile_class_name()
        self._require_sym('{')
        while self._fol_by_class_vardec():
            self.compile_class_vardec()
        while self._fol_by_subroutine():
            self.compile_subroutine()
        self._advance()
        if self._current_token != '}':
            self._traceback("Except classVarDec or subroutineDec.")
        self._write_current_terminal()

    def compile_declare(self):
        self._advance()
        self._write_current_terminal()
        # type varName (',' varName)* ';'
        self.compile_type()
        self.compile_var_name()
        # compile ',' or ';'
        self._advance()
        while self._current_token == ',':
            self._write_current_terminal()
            self.compile_var_name()
            self._advance()
        if self._current_token != ';':
            return self._error((',', ';'))
        self._write_current_terminal()

    @record_non_terminal('classVarDec')
    def compile_class_vardec(self):
        # ('static|field') type varName (',' varName)* ';'
        self.compile_declare()

    @record_non_terminal('subroutineDec')
    def compile_subroutine(self):
        # ('constructor'|'function'|'method')
        # ('void'|type) subroutineName '(' parameterList ')' subroutineBody
        self._advance()
        self._write_current_terminal()      # ('constructor'|'function'|'method')
        self.compile_void_or_type()
        self.compile_subroutine_name()
        self._require_brackets('()', self.compile_parameter_list)
        self.compile_subroutine_body()

    @record_non_terminal('parameterList')
    def compile_parameter_list(self):
        # ((type varName) (',' type varName)*)?
        if self._next_token == ')':
            return
        self.compile_type()
        self.compile_var_name()
        while self._next_token != ')':
            self._require_sym(',')
            self.compile_type()
            self.compile_var_name()

    @record_non_terminal('subroutineBody')
    def compile_subroutine_body(self):
        # '{' varDec* statements '}'
        self._require_sym('{')
        while self._fol_by_vardec():
            self.compile_vardec()
        self.compile_statements()
        self._require_sym('}')

    @record_non_terminal('varDec')
    def compile_vardec(self):
        # 'var' type varName (',' varName)* ';'
        self.compile_declare()

    #########################
    # statement compilation #
    #########################

    @record_non_terminal('statements')
    def compile_statements(self):
        # (letStatement | ifStatement | whileStatement | doStatement | 
        # returnStatement)*
        last_statement = None
        while self._next_token != '}':
            self._advance()
            last_statement = self._current_token
            if last_statement == 'do':
                self.compile_do()
            elif last_statement == 'let':
                self.compile_let()
            elif last_statement == 'while':
                self.compile_while()
            elif last_statement == 'return':
                self.compile_return()
            elif last_statement == 'if':
                self.compile_if()
            else:
                return self._error(expect='statement expression')
        if STACK[-2] == 'subroutineBody' and last_statement != 'return':
            self._error(expect='return statement', get=last_statement)

    @record_non_terminal('doStatement')
    def compile_do(self):
        # 'do' subroutineCall ';'
        self._write_current_terminal()
        # compile identifier first
        self._advance()
        self.compile_subroutine_call()
        self._require_sym(';')

    @record_non_terminal('letStatement')
    def compile_let(self):
        # 'let' varName ('[' expression ']')? '=' expression ';'
        self._write_current_terminal()
        self.compile_var_name()
        if self._next_token == '[':
            self._compile_array_subscript()
        self._require_sym('=')
        self.compile_expression()
        self._require_sym(';')

    @record_non_terminal('whileStatement')
    def compile_while(self):
        # 'while' '(' expression ')' '{' statements '}'
        self._write_current_terminal()
        self._require_brackets('()', self.compile_expression)
        self._require_brackets('{}', self.compile_statements)

    @record_non_terminal('returnStatement')
    def compile_return(self):
        # 'return' expression? ';'
        self._write_current_terminal()
        if self._next_token != ';':
            self.compile_expression()
        self._require_sym(';')

    @record_non_terminal('ifStatement')
    def compile_if(self):
        # 'if' '(' expression ')' '{' statements '}'
        # ('else' '{' statements '}')?
        self._write_current_terminal()
        self._require_brackets('()', self.compile_expression)
        self._require_brackets('{}', self.compile_statements)
        # else clause
        if self._next_token == KW_ELSE:
            self._require_kw(KW_ELSE)
            self._require_brackets('{}', self.compile_statements)

    ##########################
    # expression compilation #
    ##########################

    @record_non_terminal('expression')
    def compile_expression(self):
        # term (op term)*
        self.compile_term()
        while is_op(self._next_token):
            self.compile_op()
            self.compile_term()

    @record_non_terminal('term')
    def compile_term(self):
        # integerConstant | stringConstant | keywordConstant |
        # varName | varName '[' expression ']' | subroutineCall |
        # '(' expression ')' | unaryOp term
        if self._next_token == '(':
            self._require_brackets('()', self.compile_expression)
        elif self._next_token in set('-~'):
            self.compile_unaryop()
        else:
            self._advance()
            tok = self._current_token
            tok_type = self._current_tok_type
            if tok in self.kw_consts or tok_type in (T_INTEGER, T_STRING):
                self._write_current_terminal()
            elif tok_type == T_ID:
                if self._next_token in '(.':
                    self.compile_subroutine_call()
                else:
                    self._write_current_terminal()
                    if self._next_token == '[':
                        self._compile_array_subscript()
            else:
                self._error(expect='term')

    def compile_call_name(self):
        # the fisrt name of subroutine call could be (className or varName) if
        # it is followed by '.', or subroutineName if followed by '('.
        if self._current_tok_type != T_ID:
            self._error(expect_types=(T_ID,))
        self._write_current_terminal()
        # just write it without analysis.
        # this method will be extended to decide which kind the name is.

    def compile_subroutine_call(self):
        # subroutineName '(' expressionList ')' | (className |
        # varName) '.' subroutineName '(' expressionList ')'
        ## the first element of structure has already been compiled.
        self.compile_call_name()
        if self._next_token == '.':
            self._require_sym('.')
            self.compile_subroutine_name()
        self._require_brackets('()', self.compile_expressionlist)

    @record_non_terminal('expressionList')
    def compile_expressionlist(self):
        # (expression (',' expression)*)?
        if self._next_token != ')':
            self.compile_expression()
        while self._next_token != ')':
            self._require_sym(',')
            self.compile_expression()

    def compile_op(self):
        # exclude '~'
        self._advance()
        if self._current_token == '~':
            self._traceback('Unexpected operator: ~')
        self._write_current_terminal()

    def compile_unaryop(self):
        self._advance()
        self._write_current_terminal()      # symbol: - or ~
        self.compile_term()

    def _compile_array_subscript(self):
        # '[' expression ']'
        self._require_brackets('[]', self.compile_expression)

    def _check_EOF(self):
        if not self.tokenizer.has_more_tokens():
            self._traceback("Unexpected EOF.")

    def _error(self, expect_toks=(), expect_types=(), expect=None, get=None):
        if expect is None:
            exp_tok = ' or '.join(('"{0}"'.format(t) for t in expect_toks))
            exp_types = ('type {0}'.format(token_tags[t]) for t in expect_types)
            exp_type = ' or '.join(exp_types)
            if exp_tok and exp_type:
                expect = ' or '.join(expect_tok, expect_type)
            else:
                expect = exp_toks + exp_types
        if get is None:
            get = self._current_token
        me = 'Expect {0} but get "{1}"'.format(expect, get)
        return self._traceback(me)

    def _traceback(self, message):
        file_info = 'file: "{0}"'.format(self.tokenizer.filename)
        line_info = 'line {0}'.format(self.tokenizer.line_count)
        raise CompileError("{0}, {1}: {2}".format(file_info, line_info, message))
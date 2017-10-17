"""The CompilationEngine module provides class CompilationEngine to compile 
text in Jack language into vm language and write it into a vmfile. Jack 
language has structures:

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
from VMWriter import VMWriter

DEBUG = False
STACK = []

def record_non_terminal(non_terminal):
    def fn(procedure):
        def compile_fn(instance):
            STACK.append(non_terminal)
            if DEBUG:
                print('Compiling {0}...'.format(non_terminal))
            procedure(instance)
            STACK.pop()
        return compile_fn
    return fn

class CompileError(Exception):
    pass

class CompilationEngine:
    def __init__(self, inpath, outpath):
        self.tokenizer = Tokenizer(inpath)
        self.symboltable = SymbolTable()
        self.vmwriter = VMWriter(outpath)
        self._class_name = None
        if self.tokenizer.has_more_tokens():
            self.compile_class()
        self.vmwriter.close()
        print("{0} completed.".format(outpath))

    def _subroutine_init(self):
        self._sub_kind = None
        self._sub_name = None
        self._ret_type = None

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

    def _require_id(self):
        self._require_token(T_ID)

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

    def compile_class_name(self):
        self._require_id()
        self._class_name = self._current_token

    def compile_subroutine_name(self):
        self._require_id()
        self._sub_name = self._current_token

    def compile_var_name(self, kind=None, type=None, declare=False):
        self._require_id()
        name = self._current_token
        if declare is True:         # kind and type are not None
            self.symboltable.define(name, type, kind)
        else:
            self.check_var_name(name, type)

    def check_var_name(self, name, type=None):
        recorded_kind = self.symboltable.kindof(name)
        if recorded_kind is None:
            self._traceback('name used before declared: {0}'.format(name))
        elif type is not None:
            recorded_type = self.symboltable.typeof(name)
            if recorded_type != type:
                get = '{0} "{1}"'.format(recorded_type, name)
                self._error(expect_types=(type,), get=get)

    def compile_type(self, advanced=False, expect='type'):
        # int, string, boolean or identifier(className)
        if advanced is False:
            self._advance()
        if (self._current_token not in SymbolTable.builtIn_types 
            and self._current_tok_type != T_ID):
            return self._error(expect=expect)

    def compile_return_type(self):
        # void or type
        self._advance()
        if self._current_token != KW_VOID:
            self.compile_type(True, '"void" or type')
        self._ret_type = self._current_token
        if self._sub_kind == KW_CONSTRUCTOR and self._ret_type != self._class_name:
            me = 'constructor expect current class as return type'
            self._traceback(me)

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
            self._traceback("Except classVarDec first, subroutineDec second.")
        if self.tokenizer.has_more_tokens():
            if self._next_token == KW_CLASS:
                self._traceback('Only expect one classDec.')
            self._traceback('Unexpected extra tokens.')

    def compile_declare(self):
        self._advance()
        id_kind = self._current_token       # ('static | field | var')
        # type varName (',' varName)* ';'
        self.compile_type()
        id_type = self._current_token
        self.compile_var_name(id_kind, id_type, declare=True)
        # compile ',' or ';'
        self._advance()
        while self._current_token == ',':
            self.compile_var_name(id_kind, id_type, declare=True)
            self._advance()
        if self._current_token != ';':
            return self._error((',', ';'))

    @record_non_terminal('classVarDec')
    def compile_class_vardec(self):
        # ('static|field') type varName (',' varName)* ';'
        self.compile_declare()

    @record_non_terminal('subroutineDec')
    def compile_subroutine(self):
        # ('constructor'|'function'|'method')
        # ('void'|type) subroutineName '(' parameterList ')' subroutineBody
        self._subroutine_init()
        self.symboltable.start_subroutine()
        self._advance()
        self._sub_kind = self._current_token
        if self._sub_kind == KW_METHOD:
            self.symboltable.define('this', self._class_name, 'argument')
        self.compile_return_type()
        self.compile_subroutine_name()
        self._require_brackets('()', self.compile_parameter_list)
        self.compile_subroutine_body()

    @record_non_terminal('parameterList')
    def compile_parameter_list(self):
        # ((type varName) (',' type varName)*)?
        if self._next_token == ')':
            return
        self.compile_type()
        self.compile_var_name('argument', self._current_token, True)
        while self._next_token != ')':
            self._require_sym(',')
            self.compile_type()
            self.compile_var_name('argument', self._current_token, True)

    @record_non_terminal('subroutineBody')
    def compile_subroutine_body(self):
        # '{' varDec* statements '}'
        self._require_sym('{')
        while self._fol_by_vardec():
            self.compile_vardec()
        self.compile_function()
        self.compile_statements()
        self._require_sym('}')

    def compile_function(self):
        fn_name = '.'.join((self._class_name, self._sub_name))
        num_locals = self.symboltable.varcount(KW_VAR)
        self.vmwriter.write_function(fn_name, num_locals)       # function fn_name num_locals
        # set up pointer this
        if self._sub_kind == KW_CONSTRUCTOR:
            num_fields = self.symboltable.varcount(KW_FIELD)
            self.vmwriter.write_push('constant', num_fields)
            self.vmwriter.write_call('Memory.alloc', 1)
            self.vmwriter.write_pop('pointer', 0)
        elif self._sub_kind == KW_METHOD:
            self.vmwriter.write_push('argument', 0)
            self.vmwriter.write_pop('pointer', 0)

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
        #if STACK[-2] == 'subroutineBody' and last_statement != 'return':
        #    self._error(expect='return statement', get=last_statement)

    @record_non_terminal('doStatement')
    def compile_do(self):
        # 'do' subroutineCall ';'
        self._advance()
        self.compile_subroutine_call()
        self.vmwriter.write_pop('temp', 0)          # temp[0] store useless value
        self._require_sym(';')

    @record_non_terminal('letStatement')
    def compile_let(self):
        # 'let' varName ('[' expression ']')? '=' expression ';'
        self.compile_var_name()
        var_name = self._current_token
        array = (self._next_token == '[')
        if array:
            self.compile_array_subscript(var_name)  # push (array base + subscript)
        self._require_sym('=')
        self.compile_expression()                   # push expression value
        self._require_sym(';')
        if array:
            self.vmwriter.write_pop('temp', 1)      # pop exp value to temp[1]
            self.vmwriter.write_pop('pointer', 1)   # that = array base + subscript
            self.vmwriter.write_push('temp', 1)
            self.vmwriter.write_pop('that', 0)
        else:
            self.assign_variable(var_name)

    kind_segment = {'static': 'static', 'field': 'this',
                    'argument': 'argument', 'var': 'local'}

    def assign_variable(self, name):
        kind = self.symboltable.kindof(name)
        index = self.symboltable.indexof(name)
        self.vmwriter.write_pop(self.kind_segment[kind], index)

    def load_variable(self, name):
        kind = self.symboltable.kindof(name)
        index = self.symboltable.indexof(name)
        self.vmwriter.write_push(self.kind_segment[kind], index)

    label_num = 0

    @record_non_terminal('whileStatement')
    def compile_while(self):
        # 'while' '(' expression ')' '{' statements '}'
        start_label = 'WHILE_START_' + str(self.label_num)
        end_label = 'WHILE_END_' + str(self.label_num)
        self.label_num += 1
        self.vmwriter.write_label(start_label)
        self.compile_cond_expression(start_label, end_label)

    @record_non_terminal('ifStatement')
    def compile_if(self):
        # 'if' '(' expression ')' '{' statements '}'
        # ('else' '{' statements '}')?
        else_label = 'IF_ELSE_' + str(self.label_num)
        end_label = 'IF_END_' + str(self.label_num)
        self.label_num += 1
        self.compile_cond_expression(end_label, else_label)
        # else clause
        if self._next_token == KW_ELSE:
            self._require_kw(KW_ELSE)
            self._require_brackets('{}', self.compile_statements)
        self.vmwriter.write_label(end_label)

    def compile_cond_expression(self, goto_label, end_label):
        self._require_brackets('()', self.compile_expression)
        self.vmwriter.write_arithmetic('not')
        self.vmwriter.write_if(end_label)
        self._require_brackets('{}', self.compile_statements)
        self.vmwriter.write_goto(goto_label)        # meet
        self.vmwriter.write_label(end_label)

    @record_non_terminal('returnStatement')
    def compile_return(self):
        # 'return' expression? ';'
        if self._sub_kind == KW_CONSTRUCTOR:
            self._require_kw(KW_THIS)       # constructor must return 'this'
            self.vmwriter.write_push('pointer', 0)
        elif self._next_token != ';':
            self.compile_expression()
        else:
            if self._ret_type != KW_VOID:
                self._traceback('expect return ' + self._ret_type)
            self.vmwriter.write_push('constant', 0)
        self._require_sym(';')
        self.vmwriter.write_return()

    ##########################
    # expression compilation #
    ##########################

    unary_ops = {'-': 'neg', '~': 'not'}
    binary_ops = {'+': 'add', '-': 'sub', '*': None, '/': None, 
                  '&': 'and', '|': 'or', '<': 'lt', '>': 'gt', '=': 'eq'}

    @record_non_terminal('expression')
    def compile_expression(self):
        # term (op term)*
        self.compile_term()
        while self._next_token in self.binary_ops:
            self._advance()
            if self._current_tok_type != T_SYMBOL:
                self._error(expect_types=(T_SYMBOL,))
            op = self._current_token
            self.compile_term()
            self.compile_binaryop(op)

    def compile_binaryop(self, op):
        if op == '*':
            self.vmwriter.write_call('Math.multiply', 2)
        elif op == '/':
            self.vmwriter.write_call('Math.divide', 2)
        else:
            self.vmwriter.write_arithmetic(self.binary_ops[op])

    kw_consts = (KW_TRUE, KW_FALSE, KW_NULL, KW_THIS)

    @record_non_terminal('term')
    def compile_term(self):
        # integerConstant | stringConstant | keywordConstant |
        # varName | varName '[' expression ']' | subroutineCall |
        # '(' expression ')' | unaryOp term
        if self._next_token == '(':
            self._require_brackets('()', self.compile_expression)
        else:
            self._advance()
            tok = self._current_token
            tok_type = self._current_tok_type
            if tok_type == T_KEYWORD and tok in self.kw_consts:
                self.compile_kw_consts(tok)
            elif tok_type == T_INTEGER:
                self.vmwriter.write_push('constant', tok)
            elif tok_type == T_STRING:
                self.compile_string(tok)
            elif tok_type == T_ID:
                if self._next_token in '(.':
                    self.compile_subroutine_call()
                elif self._next_token == '[':
                    self.check_var_name(tok)
                    self.compile_array_subscript(tok)
                    self.vmwriter.write_pop('pointer', 1)
                    self.vmwriter.write_push('that', 0)
                else:
                    self.check_var_name(tok)
                    self.load_variable(tok)
            elif tok_type == T_SYMBOL and tok in self.unary_ops:
                self.compile_term()
                self.vmwriter.write_arithmetic(self.unary_ops[tok])
            else:
                self._error(expect='term')

    # keywordConstant: 'true' | 'false' | 'null' | 'this'
    def compile_kw_consts(self, kw):
        if kw == KW_THIS:
            self.vmwriter.write_push('pointer', 0)
        if kw == KW_TRUE:
            self.vmwriter.write_push('constant', 1)
            self.vmwriter.write_arithmetic('neg')
        else:
            self.vmwriter.write_push('constant', 0)

    def compile_string(self, string):
        self.vmwriter.write_push('constant', len(string))
        self.vmwriter.write_call('String.new', 1)
        for char in string:
            self.vmwriter.write_push('constant', ord(char))
            self.vmwriter.write_call('String.appendChar', 2)

    def compile_subroutine_call(self):
        # subroutineName '(' expressionList ')' |
        # (className | varName) '.' subroutineName '(' expressionList ')'
        ## the first element of structure has already been compiled.
        fn_name = self.compile_call_name()
        self._require_brackets('()', self.compile_expressionlist)
        self.vmwriter.write_call(fn_name, self._num_args)

    def compile_call_name(self):
        # the fisrt name of subroutine call could be (className or varName) if
        # it is followed by '.', or subroutineName if followed by '('.
        if self._current_tok_type != T_ID:
            self._error(expect_types=(T_ID,))
        self._num_args = 0              # num of arguments that subroutine has
        name = self._current_token
        if self._next_token == '.':
            self._require_sym('.')
            self.compile_subroutine_name()
            sub_name = self._current_token
            if (name in self.symboltable.all_class_types() or 
                name in SymbolTable.builtIn_class or
                name == self._class_name):
                return '.'.join((name, sub_name))       # className
            else:
                self.check_var_name(name)               # varName with class type
                type = self.symboltable.typeof(name)
                if type in SymbolTable.builtIn_types:
                    return self._error(expect='class instance or class', get=type)
                self.load_variable(name)
                #self.vmwriter.write_push('pointer', 0)      # push this to be 1st arg
                self._num_args += 1
                return '.'.join((type, sub_name))
        elif self._next_token == '(':
            self.vmwriter.write_push('pointer', 0)      # push this to be 1st arg
            self._num_args += 1
            return '.'.join((self._class_name, name))   # subroutineName

    @record_non_terminal('expressionList')
    def compile_expressionlist(self):
        # (expression (',' expression)*)?
        if self._next_token != ')':
            self.compile_expression()
            self._num_args += 1
        while self._next_token != ')':
            self._require_sym(',')
            self.compile_expression()
            self._num_args += 1

    def compile_array_subscript(self, var_name):
        # varName '[' expression ']'
        self.check_var_name(var_name, 'Array')
        self._require_brackets('[]', self.compile_expression)   # push expression value
        self.load_variable(var_name)
        self.vmwriter.write_arithmetic('add')   # base + subscript

    def _check_EOF(self):
        if not self.tokenizer.has_more_tokens():
            self._traceback("Unexpected EOF.")

    def _error(self, expect_toks=(), expect_types=(), expect=None, get=None):
        if expect is None:
            exp_tok = ' or '.join(('"{0}"'.format(t) for t in expect_toks))
            exp_types = ('type {0}'.format(token_tags[t]) for t in expect_types)
            exp_type = ' or '.join(exp_types)
            if exp_tok and exp_type:
                expect = ' or '.join(exp_tok, exp_type)
            else:
                expect = exp_tok + exp_type
        if get is None:
            get = self._current_token
        me = 'Expect {0} but get "{1}"'.format(expect, get)
        return self._traceback(me)

    def _traceback(self, message):
        if DEBUG:
            print('--------------------------------------------')
            print(self.symboltable)
            print(self.symboltable.all_class_types())
            print('--------------------------------------------')
        file_info = 'file: "{0}"'.format(self.tokenizer.filename)
        line_info = 'line {0}'.format(self.tokenizer.line_count)
        raise CompileError("{0}, {1}: {2}".format(file_info, line_info, message))

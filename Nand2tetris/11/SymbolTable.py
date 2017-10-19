"""The SymbolTable module provides class SymbolTable for combining the symbols
with their attributes (type, kind, index) during compilation of Jack language.
There are two kinds of scopes in Jack language:

  * class scope
  * subroutine scope (including method, function and constructor)

"""

from JackDefinitions import *

class SymbolError(Exception):
    pass

def make_segment(type, kind, index):
    return (type, kind, index)

def seg_type(seg):
    return seg[0]

def seg_kind(seg):
    return seg[1]

def seg_index(seg):
    return seg[2]

def is_class_kind(kind):
    return kind in ('static', 'field')

def is_subroutine_kind(kind):
    return kind in ('argument', 'var')

class SymbolTable:
    builtIn_class = ('Array', 'Keyboard', 'Math', 'Memory', 
                     'Output', 'Screen', 'String', 'Sys')
    builtIn_types = (KW_INT, KW_CHAR, KW_BOOLEAN)

    def __init__(self):
        self.class_scope = {}
        self.sub_scope = {}
        self.index_count = {'static': 0, 'field': 0, 'argument': 0, 'var': 0}

    def __str__(self):
        string = 'class scope: {0}\nsubroutine scope: {1}\n'
        return string.format(self.class_scope, self.sub_scope)

    def all_class_types(self):
        # extra method for className check
        segs = list(self.class_scope.values()) + list(self.sub_scope.values())
        return set(seg_type(s) for s in segs if seg_type(s) not in self.builtIn_types)

    def start_subroutine(self):
        self.sub_scope.clear()
        self.index_count['argument'] = self.index_count['var'] = 0

    def define(self, name, type, kind):
        # static, field: class scope
        # arg, var: subroutine scope
        if is_class_kind(kind):
            self.class_scope[name] = make_segment(type, kind, self.index_count[kind])
        elif is_subroutine_kind(kind):
            self.sub_scope[name] = make_segment(type, kind, self.index_count[kind])
        else:
            raise SymbolError('expect kind "static", "field", "argument", or "var"')
        self.index_count[kind] += 1

    def varcount(self, kind):
        return self.index_count[kind]

    def kindof(self, name):
        return self._name_info(name, seg_kind, report=False)

    def typeof(self, name):
        return self._name_info(name, seg_type)

    def indexof(self, name):
        return self._name_info(name, seg_index)

    def _name_info(self, name, info_func, report=True):
        # check subroutine scope first, class scope second.
        if name in self.sub_scope:
            return info_func(self.sub_scope[name])
        elif name in self.class_scope:
            return info_func(self.class_scope[name])
        elif report is True:
            raise SymbolError('Symbol not defined.')
        else:
            return None

def test():
    st = SymbolTable()
    test_infos = [('nAccounts', 'int', 'static'), 
                  ('bankCommission', 'int', 'static'),
                  ('id', 'int', 'field'),
                  ('owner', 'string', 'field'),
                  ('balance', 'int', 'field'),
                  ('this', 'BankAccount', 'argument'),
                  ('sum', 'int', 'argument'),
                  ('from', 'BankAccount', 'argument'),
                  ('when', 'Date', 'argument'),
                  ('i', 'int', 'var'),
                  ('j', 'int', 'var'),
                  ('due', 'Date', 'var')]
    for info in test_infos:
        st.define(*info)
    print(st)
    print(st.all_class_types())
    st.start_subroutine()
    print(st)

if __name__ == '__main__':
    test()

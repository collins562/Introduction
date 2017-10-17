"""The JackTokenizer module provides class Tokenizer for converting (iterators
producing) strings into (iterators producing) lists of tokens. A token may be:

  * A keyword (represented as a predefined word)
  * A symbol (represented as a delimiter or an operator)
  * A identifier (represented as a classname, subroutinename or varname)
  * A int constant (represented as a int)
  * A string constant (represented as a string)

"""

import os
import string
import tokenize
from JackDefinitions import *

SYMBOLS = set(symbols)
_STRING_DELIMS = set('"')
_IDENTIFIER_STARTS = (set(string.ascii_lowercase) | set(string.ascii_uppercase) |
                      set('_'))
_IDENTIFIER_CHARS = _IDENTIFIER_STARTS | set(string.digits)
_WHITESPACE = set(' \t\n\r')
_TOKEN_END = _WHITESPACE | _STRING_DELIMS | SYMBOLS | set('\\')

def valid_id(s):
    if len(s) == 0 or s[0] not in _IDENTIFIER_STARTS:
        return False
    for char in s[1:]:
        if char not in _IDENTIFIER_CHARS:
            return False
    return True

def next_candidate_token(line, k, comment=False):
    """A tuple (tok, k', comment), where tok is the next substring of line 
    at or after position k that could be a token (assuming it passes a 
    validity check); k' is the position in line following that token; and
    comment indicates if there is any comment. Returns (None, len(line), 
     comment) when there are no more tokens."""
    length = len(line)
    if comment:
        if '*/' not in line[k:]:
            return None, length, comment
        return next_candidate_token(line, line.find('*/')+2)
    while k < length:
        c = line[k]
        if c == '/' and k+1 < length:      # comment or operator
            next_char = line[k+1]
            if next_char == '/':
                return None, length, comment
            elif next_char == '*':
                return next_candidate_token(line, k+2, True)
        if c in _WHITESPACE:
            k += 1
        elif c in SYMBOLS:
            return c, k+1, comment
        elif c in _STRING_DELIMS:
            if k+1 < length and line[k+1] == c: # No triple quotes in Jack
                return c+c, k+2, comment
            line_bytes = (bytes(line[k:], encoding='utf-8'),)
            gen = tokenize.tokenize(iter(line_bytes).__next__)
            next(gen) # Throw away encoding token
            token = next(gen)
            if token.type != tokenize.STRING:
                report_error("invalid string: {0}".format(token.string), line, k)
            return token.string, token.end[1]+k, comment
        else:
            j = k
            while j < length and line[j] not in _TOKEN_END:
                j += 1
            return line[k:j], j, comment
    return None, length, comment

def tokenize_line(line, comment=False):
    """return the list of Jack tokens on line and comment that indicate that 
    there is any comment in current line. Excludes comments."""
    result = []
    text, i, comment = next_candidate_token(line, 0, comment)
    while text is not None and not comment:
        if text in SYMBOLS:
            result.append(text)
        elif text[0] in _STRING_DELIMS:
            result.append(text)
        elif text[0].isdigit() and is_integer(text):
            result.append(int(text))
        else:
            if not valid_id(text):
                report_error("invalid identifier", line, i-len(text))
            result.append(text)
        text, i, comment = next_candidate_token(line, i)
    return result, comment

def tokenize_lines(input):
    """Return a iterable of tokens, one for each line of the iterable input
    sequence. Exclude whitespace (include the whitespace between two words)"""
    comment = False
    for line in input:
        tokens, comment = tokenize_line(line, comment)
        yield tokens

def report_error(message, line, i):
    raise ValueError("%s:\n%s%s" %(message, "    "+line, " "*(i+4)+"^"))



class TokenError(Exception):
    pass

class Tokenizer:
    def __init__(self, path):
        if not path.endswith('.jack'):
            raise TokenError("Expect a jack file.")
        with open(path, 'r') as file:
            self.token_lines = tokenize_lines(file.readlines())
        self.token = None
        self.token_type = None
        self.filename = os.path.basename(path)      # filename for traceback
        self.line_count = 0         # line_count for traceback in compilation
        self._newline_count = 1     # normally change 1 newline at a time
        self._update_line_toks()    # to get the first tokens line
        self._update_next_token()   # to get the first token in input stream

    def mark_start(self, toks):
        """Take in a list of tokens and return it with marks of which one token
        is the head of line."""
        return [(True, toks[0])] + [(False, t) for t in toks[1:]] if toks else []

    def is_head(self, tok):
        return self._next_tok[0]

    @property
    def next_token(self):
        return self._next_tok[1] if self._next_tok is not None else None

    def _update_next_token(self):
        """Update the next_tok for checking if there is any token left"""
        if self._line_toks is None:
            self._next_tok = None
        else:
            self._next_tok = self._line_toks.pop(0)
            if self._line_toks == []:
                self._update_line_toks()

    def _update_line_toks(self):
        """Update line_toks for the update of next_token. """
        try:
            self._line_toks = self.mark_start(next(self.token_lines))
            if self._line_toks == []:
                self._newline_count += 1
                self._update_line_toks()
        except StopIteration:
            self._line_toks = None

    def _detect_type(self):
        return (T_KEYWORD if is_keyword(self.token) else
                T_SYMBOL  if is_symbol(self.token)  else
                T_INTEGER if is_integer(self.token) else
                T_STRING  if is_string(self.token)  else
                T_ID)

    def has_more_tokens(self):
        return self.next_token is not None

    def advance(self):
        if not self.has_more_tokens():
            raise TokenError("There are no more tokens.")
        self.token = self.next_token
        self.token_type = self._detect_type()
        if self.is_head(self._next_tok):
            self.line_count += self._newline_count
            self._newline_count = 1
        self._update_next_token()

    @property
    def keyword(self):
        assert self.token_type == T_KEYWORD
        return self.token

    @property
    def symbol(self):
        assert self.token_type == T_SYMBOL
        return self.token

    @property
    def identifier(self):
        assert self.token_type == T_ID
        return self.token

    @property
    def intval(self):
        assert self.token_type == T_INTEGER
        return self.token

    @property
    def stringval(self):
        assert self.token_type == T_STRING
        return self.token[1:-1]

def test_line_count():
    tokenizer = Tokenizer('ArrayTest/main.jack')
    line = 0
    while tokenizer.has_more_tokens():
        tokenizer.advance()
        if tokenizer.line_count != line:
            line = tokenizer.line_count
            print("\nline {0}: ".format(line), end='')
        print(tokenizer.token, end=' ')

if __name__ == '__main__':
    test_line_count()

"""The hdl_tokens module provides functions tokenize_line and tokenize_lines
for converting (iterators producing) strings into (iterators producing) lists
of tokens. A token may be:

  * A constant (represented as an positive int)
  * A symbol (represented as a string)
  * A delimiter ('=', ';', '/', '(', ')')
  * A operator ('@', '!', '-', '+', '&', '|')
  * A mnemonic (represented as an uppercase string)

"""

import string

_CONSTANT = set(string.digits)
_SYMBOL_STARTS = (set('_.$:') | set(string.ascii_lowercase) |
				  set(string.ascii_uppercase))
_SYMBOL_CHARS = _SYMBOL_STARTS | _CONSTANT
_SINGLE_CHAR_TOKENS = set('@()=;')
_COMMENT_DELIMS = set('/')
_TOKEN_END = set('=;') | _COMMENT_DELIMS | _SINGLE_CHAR_TOKENS
_WHITESPACE = set(' \t\n\r')

def next_token(line, k):
	"""A tuple (tok, k'), where tok is the next substring of line at or
	after position k that could be a token (assuming it passes a validity
	check), and k' is the position in line following that token.  Returns
	(None, len(line)) when there are no more tokens."""
	length = len(line)
	while k < length:
		c = line[k]
		if c == '/':      # comment
			if k+1 < length and line[k+1] == '/':
				return None, length
			report_error("Invalid Comment", line, k)
		elif c in _WHITESPACE:
			k += 1
		elif c in _SINGLE_CHAR_TOKENS:
			return c, k+1
		else:
			text, j = c, k+1
			while j < length and line[j] not in _TOKEN_END:
				if line[j] not in _WHITESPACE:
					text += line[j]
				j += 1
			return text, j
	return None, length

def tokenize_line(line):
	"""The list of HDL tokens on line. Excludes comments and whitespace."""
	result = []
	pre_text = None
	text, i = next_token(line, 0)
	while text is not None:
		if pre_text == '@' and not (text.isdigit() or valid_symbol(text)):
			report_error("Illegal Symbol", line, i-len(text))
		elif pre_text == '(':
			if text == ')':
				report_error("Need symbol", line, i-1)
			elif not valid_symbol(text):
				report_error("Illegal Symbol", line, i-len(text))
		result.append(text)
		pre_text = text
		text, i = next_token(line, i)
	return result

def tokenize_lines(input):
	"""Return a iterable of tokens, one for each line of the iterable input
	sequence. Exclude whitespace (include the whitespace between two words)"""
	return map(tokenize_line, input)

def report_error(message, line, i):
    raise SyntaxError("{}:\n{}\n{}".format(message, "    "+line, " "*(i+4)+"^"))

def valid_symbol(text):
	"""return whether text is well-formed symbol or not"""
	if text[0] not in _SYMBOL_STARTS:
		return False
	for char in text:
		if char not in _SYMBOL_CHARS:
			return False
	return True

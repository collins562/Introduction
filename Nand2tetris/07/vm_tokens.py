"""The vm_tokens module provides functions tokenize_line and tokenize_lines
for converting (iterators producing) strings into (iterators producing) lists
of tokens. A token may be:

  * An instruction (represented as stack instruction or
  								   arithmetic instruction or
  								   program flow instruction or
  								   function calling instruction)
  * A segment (represented as memory segment)
  * A constant (represented as an positive int)
  * A symbol

"""

import string

_INST_WITH_LABEL = ('label', 'goto', 'if-goto', 'function', 'call')
_CONSTANT = set(string.digits)
_SYMBOL_STARTS = (set('_.$:') | set(string.ascii_lowercase) |
				  set(string.ascii_uppercase))
_SYMBOL_CHARS = _SYMBOL_STARTS | _CONSTANT
_WHITESPACE = set(' \t\n\r')
_INST_CHARS = _SEGMENT_CHARS = set(string.ascii_lowercase)
_TOKEN_END = _WHITESPACE | set('/')

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
			report_error("Invalid Comment:", line, k)
		elif c in _WHITESPACE:
			k += 1
		else:
			j = k
			while j < length and line[j] not in _TOKEN_END:
				j += 1
			return line[k:j], j
	return None, length

def tokenize_line(line):
	"""The list of VM tokens on line. Excludes comments."""
	result = []
	text, i = next_token(line, 0)
	while text is not None:
		if len(result) == 1 and result[0] in _INST_WITH_LABEL:
			if not valid_symbol(text):
				report_error("Illegal symbol", line, i-len(text))
		result.append(text)
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

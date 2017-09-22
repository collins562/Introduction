"""The hdl_tokens module provides functions tokenize_line and tokenize_lines
for converting (iterators producing) strings into (iterators producing) lists
of tokens. A token may be:

  * A constant (represented as an positive int)
  * A symbol (represented as a string)
  * A delimiter ('=', ';', '/')
  * A operator ('@', '!', '-', '+', '&', '|')
  * A mnemonic (represented as an uppercase string)

"""

import string
from Code import COMP_CODES

_CONSTANT = set(string.digits)
_SYMBOL_STARTS = (set('_.$:') | set(string.ascii_lowercase) |
				  set(string.ascii_uppercase))
_SYMBOL_CHARS = _SYMBOL_STARTS | _CONSTANT
_COMMENT_DELIMS = set('/')
_TOKEN_END = set('=;') | _COMMENT_DELIMS

def next_token(line, k):
	"""A tuple (tok, k'), where tok is the next substring of line at or
	after position k that could be a token (assuming it passes a validity
	check), and k' is the position in line following that token.  Returns
	(None, len(line)) when there are no more tokens."""
	length = len(line)
	if k >= length:
		return None, length
	c = line[k]
	if c == '/':      # comment
		if k+1 < length and line[k+1] == '/':
			return None, length
		report_error("Invalid Comment:", line, k)
	elif c == '@':    # A_command
		return _tokenize(line, c, k, _COMMENT_DELIMS)
	elif c == '(':    # L_command
		return _tokenize(line, c, k, _COMMENT_DELIMS)
	else:             # C_command
		text, i = _tokenize(line, c, k, _TOKEN_END)
		if i < length and line[i] == '=':
			return text + '=', i + 1
		return text, i

def _tokenize(line, c, k, END):
	text, i = c, k+1
	while i < len(line) and line[i] not in END:
		text += line[i]
		i += 1
	return text, i

def tokenize_line(line):
	"""The list of HDL tokens on line. Excludes comments."""
	text, i = next_token(line, 0)
	if text == None:
		return None
	# @constant or @symbol
	if text[0] == '@':
		return ('a_command', text[1:] 
				if valid_const(text[1:]) or valid_symbol(text[1:])
				else report_error("Invalid syntax:", line, 1))
	# (symbol)
	elif text[0] == '(':
		return ('l_command', text[1:-1] 
				if valid_symbol(text[1:-1])
				else report_error("Invalid label:", line, 1))
	# c_command:
	# dest=comp;jump
	# comp;jump
	# dest=comp
	# comp
	C_parts = init_C_parts()
	while text is not None:
		if is_dest(text):
			C_parts['dest'] = command_dest(text, line, i-1)
		elif is_jump(text):
			C_parts['jump'] = command_jump(text, line, i-1)
		elif is_comp(text):
			C_parts['comp'] = text
		else:
			report_error("Invalid command form:", line, i)
		text, i = next_token(line, i)
	return ('c_command', C_parts if has_comp(C_parts) else
			report_error("Need comp:", line, 0))

def tokenize_lines(input):
	"""Return a iterable of tokens, one for each line of the iterable input
	sequence. Exclude whitespace (include the whitespace between two words)"""
	return filter((lambda r: r is not None),
				  (tokenize_line(line.strip().replace(' ', ''))
				   for line in input))

def report_error(message, line, i):
    print(message)
    print("    ", line)
    print(" " * (i+4), "^")
    #raise SyntaxError

def valid_const(text):
	"""return whether text is well-formed constant or not"""
	return text.isdigit()

def valid_symbol(text):
	"""return whether text is well-formed symbol or not"""
	if text[0] not in _SYMBOL_STARTS:
		return False
	for char in text:
		if char not in _SYMBOL_CHARS:
			return False
	return True

def init_C_parts():
	return {'dest': 'null', 'comp': None, 'jump': 'null'}

def command_type(command):
	return command[0]

def command_content(command):
	return command[1]

def is_dest(text):
	return text[-1] == '='

def is_jump(text):
	return text[0] == ';'

def is_comp(text):
	return text in COMP_CODES

def command_dest(text, line, k):
	return (report_error("Invalid syntax", line, k) 
			if text[:-1] == '' else text[:-1])

def command_jump(text, line, k):
	return (report_error("Invalid syntax", line, k) 
			if text[1:] == '' else text[1:])

def has_comp(parts):
	return parts['comp'] is not None

def test_tokenize_lines():
	lines = ['// Symbol-less version of the Max.asm program.', 
 	 		 '', '@0', 'D=M', '@1', 'D=D-M', '@10', 
	 		 'D;JGT', '@1', 'D=M', '@12', '0;JMP', 
 	 		 '@0', 'D=M', '@2', 'M=D', '@14', '0;JMP']
	assert list(tokenize_lines(lines)) == \
			   [('a_command', '0'),
				('c_command', {'comp': 'M', 'dest': 'D', 'jump': 'null'}),
				('a_command', '1'),
				('c_command', {'comp': 'D-M', 'dest': 'D', 'jump': 'null'}),
				('a_command', '10'),
				('c_command', {'comp': 'D', 'dest': 'null', 'jump': 'JGT'}),
				('a_command', '1'),
				('c_command', {'comp': 'M', 'dest': 'D', 'jump': 'null'}),
				('a_command', '12'),
				('c_command', {'comp': '0', 'dest': 'null', 'jump': 'JMP'}),
				('a_command', '0'),
				('c_command', {'comp': 'M', 'dest': 'D', 'jump': 'null'}),
				('a_command', '2'),
				('c_command', {'comp': 'D', 'dest': 'M', 'jump': 'null'}),
				('a_command', '14'),
				('c_command', {'comp': '0', 'dest': 'null', 'jump': 'JMP'})]
	print("Test passed.")

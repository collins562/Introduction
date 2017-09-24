"""
implement a parser to parse the hdl language.
The function of parser in this file would be as follow:

>>> p = Parser('rect/Rect.asm')
>>> while p.has_more_commands():
... 	p.advance()
... 	print("line %2s: <%s> %s" %(p._current_line, 
... 								p.command_type, 
... 								p.current))

line  9: <a_command> ['@', '0']
line 10: <c_command> ['D', '=', 'M']
line 11: <a_command> ['@', 'INFINITE_LOOP']
line 12: <c_command> ['D', ';', 'JLE']
line 13: <a_command> ['@', 'counter']
line 14: <c_command> ['M', '=', 'D']
line 15: <a_command> ['@', 'SCREEN']
line 16: <c_command> ['D', '=', 'A']
line 17: <a_command> ['@', 'address']
line 18: <c_command> ['M', '=', 'D']
line 19: <l_command> ['(', 'LOOP', ')']
line 20: <a_command> ['@', 'address']
line 21: <c_command> ['A', '=', 'M']
line 22: <c_command> ['M', '=', '-1']
line 23: <a_command> ['@', 'address']
line 24: <c_command> ['D', '=', 'M']
line 25: <a_command> ['@', '32']
line 26: <c_command> ['D', '=', 'D+A']
line 27: <a_command> ['@', 'address']
line 28: <c_command> ['M', '=', 'D']
line 29: <a_command> ['@', 'counter']
line 30: <c_command> ['MD', '=', 'M-1']
line 31: <a_command> ['@', 'LOOP']
line 32: <c_command> ['D', ';', 'JGT']
line 33: <l_command> ['(', 'INFINITE_LOOP', ')']
line 34: <a_command> ['@', 'INFINITE_LOOP']
line 35: <c_command> ['0', ';', 'JMP']
"""

from hdl_tokens import *
import Code

class NoMoreCommandError(IndexError):
	pass

class CommandError(TypeError):
	pass

class Parser(object):
	"""
	Take in a path of hdl file, get rid of the whitespace and comments of 
	the content and parse each command's type and parts.
	"""
	def __init__(self, path):
		self.current = None
		self._initial(path)

	def _initial(self, path):
		with open(path, 'r') as file:
			self.commands = tokenize_lines(file.readlines())
		self._current_file = path
		self._current_line = -1
		self._next()

	def _next(self):
		try:
			self._next_command = next(self.commands)
		except StopIteration:
			self._next_command = None
		finally:
			self._current_line += 1
		if self._next_command == []:
			self._next()

	def has_more_commands(self):
		return self._next_command is not None

	def advance(self):
		if self.has_more_commands():
			self.current = self._next_command
			self._next()
		else:
			raise NoMoreCommandError('There is no more commands.')

	@property
	def command_type(self):
		text = ''.join(self.current)
		if self.current[0] == '@':
			self.check_a_command(text)
			return 'a_command'				
		elif self.current[0] == '(':
			self.check_l_command(text)
			return 'l_command'
		else:
			self.check_c_command(text)
			return 'c_command'
			
	def check_a_command(self, text):
		if len(self.current) < 2:
			self._trackback("Need a address or symbol.")
		elif len(self.current) > 2:
			self._trackback("Invalid Syntax: " + ''.join(self.current[2:]))

	def check_l_command(self, text):
		if self.current[-1] != ')':
			self._trackback("Invalid Syntax: " + text)
		elif len(self.current[1:-1]) > 1:
			self._trackback("Invalid Syntax: " + text)

	def check_c_command(self, text):
		if text in ('=', ';'):
			self._trackback("Expression expected.")
		if (any(e in self.current for e in '@()') or
			self.current.count('=') > 1 or 
			self.current.count(';') > 1):
			self._trackback("Invalid Syntax: " + text)
		i1, i2 = None, None
		if '=' in self.current:
			i1 = self.current.index('=')
		if ';' in self.current:
			i2 = self.current.index(';')
		if ((i1 and (i1 not in (0, 1) or len(self.current) == i1+1)) or 
			(i2 and (i2 not in range(len(self.current)-2, 5) or i2 == 0)) or
			(i1 and i2 and (i1 > i2 or i2 - i1 == 1))):
			self._trackback("Invalid Syntax: " + text)

	def _trackback(self, me):
		raise CommandError('file "%s", line %s: %s'
						   %(self._current_file, self._current_line, me))

	@property
	def symbol(self):
		if self.command_type == 'a_command' or self.command_type == 'l_command':
			return self.current[1]
		else:
			raise CommandError('Current command has no symbol: '+str(self.current))

	@property
	def dest(self):
		assert self.command_type == 'C_COMMAND'
		if '=' in self.current and self.current != '=':
			if self.current[0] not in Code.DEST_CODES:
				self._trackback("Unknown destination.")
			return self.current[0]
		return 'null'

	@property
	def comp(self):
		assert self.command_type == 'C_COMMAND'
		if '=' in self.current:
			comp = self.current[self.current.index('=')+1]
		else:
			comp = self.current[0]
		if comp not in Code.COMP_CODES:
			self._trackback("Unknown expression")
		return comp

	@property
	def jump(self):
		assert self.command_type == 'C_COMMAND'
		if ';' in self.current and self.current[-1] != ';':
			if self.current[-1] not in Code.JUMP_CODES:
				self._trackback("Jump directive expected")
			return self.current[-1]
		return 'null'

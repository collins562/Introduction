"""The Parser module load the vm commands from file, parse them, and
provide access for the parts of commands. Excludes whitespace and comments.
An error-handling system is implemented.

The function would be like:

>>> p = Parser('MemoryAccess/BasicTest/BasicTest.vm')
>>> p.advance()
>>>	print("line %s: <Type %s> <arg1: %s> <arg2: %s>" %
		  (p._current_line, p.command_type, p.arg1, p.arg2))
line 7: <Type 2> <arg1: constant> <arg2: 10>

"""

import os
from vm_tokens import *
from vm_primitives import *

class NoMoreCommandError(IndexError):
	pass

class CommandError(TypeError):
	pass

class Parser(object):
	"""
	Take in a path of vm file, exclude the whitespace and comments of 
	the content and parse each command's type and parts.
	"""
	def __init__(self, path):
		self.current = None
		self._c_type = None
		self._initial(path)

	def _initial(self, path):
		with open(path, 'r') as file:
			self.commands = tokenize_lines(file.readlines())
		self._current_file = os.path.split(path)[-1]
		self._current_line = -1
		self._next()

	def _next(self):
		"""update next_command if there is more commands(ignore the empty
		command), or reset it to None. Update the current_line for 
		traceback"""
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
			self._c_type = self._detect_type(self.current)
			self._next()
		else:
			raise NoMoreCommandError("There is no more commands.")

	def _detect_type(self, command):
		"""detect command type such as:
				C_ERROR, C_ARITH, C_PUSH, C_POP, C_GOTO, 
				C_IF, C_FUNCTION, C_RETURN, C_CALL
		report an error when command type is C_ERROR."""
		c_type, me = check_command(command)
		if c_type == C_ERROR:
			self._traceback(me)
		return c_type

	@property
	def command_type(self):
		return self._c_type

	@property
	def arg1(self):
		assert self.command_type != C_RETURN
		if self.command_type == C_ARITHMETIC:
			return self.current[0]
		else:
			return self.current[1]

	@property
	def arg2(self):
		assert self.command_type in (C_PUSH, C_POP, C_FUNCTION, C_CALL)
		return self.current[2]

	def _traceback(self, me):
		raise CommandError('file "%s", line %s: %s'
						   %(self._current_file, self._current_line, me))

from hdl_tokens import *

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
		self._next()

	def _next(self):
		try:
			self._next_command = next(self.commands)
		except StopIteration:
			self._next_command = None

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
		return command_type(self.current)

	@property
	def symbol(self):
		if self.command_type == 'a_command' or self.command_type == 'l_command':
			return command_content(self.current)
		else:
			raise CommandError('Current command has no symbol: '+str(self.current))

	@property
	def dest(self):
		assert self.command_type == 'C_COMMAND'
		return command_content(self.current)['dest']

	@property
	def comp(self):
		assert self.command_type == 'C_COMMAND'
		return command_content(self.current)['comp']

	@property
	def jump(self):
		assert self.command_type == 'C_COMMAND'
		return command_content(self.current)['jump']

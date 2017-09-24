"""
for assembling the hdl codes with symbols.
"""

from Parser import Parser
from Code import *
from SymbolTable import SymbolTable

class Assembler:
	def __init__(self):
		self._initial()

	def _initial(self):
		self.symbols = SymbolTable()
		self.next_addr = 16

	def assemble(self, path, dest=None):
		if dest is None:
			dest = path.rsplit('.')[0] + '.hack'
		p = Parser(path)
		with open(dest, 'w') as target:
			for cm in self.extract_labels(p):
				tag, parts = cm
				if tag == 'a_command':
					bits = complete_A(self.get_address(parts))
					target.write(bits + '\n')
				elif tag == 'c_command':
					bits = complete_C(parts[0], parts[1], parts[2])
					target.write(bits + '\n')
		self._initial()

	def extract_labels(self, p):
		"""Extract the labels out of commands and return the rest commands (A and
		C commands)."""
		rom_address = 0
		rest_commands = []
		while p.has_more_commands():
			p.advance()
			cm_type = p.command_type
			if cm_type == 'l_command':
				self.symbols.add_entry(p.symbol, rom_address)
			elif cm_type == 'a_command':
				rest_commands.append((cm_type, p.symbol))
				rom_address += 1
			elif cm_type == 'c_command':
				rest_commands.append((cm_type, (p.dest, p.comp, p.jump)))
				rom_address += 1
		return rest_commands

	def get_address(self, symbol):
		if symbol.isdigit():
			return symbol
		if not self.symbols.contains(symbol):
			self.symbols.add_entry(symbol, self.next_addr)
			self.next_addr += 1
		return self.symbols.get_address(symbol)

if __name__ == '__main__':
	a = Assembler()
	a.assemble('max/Max.asm')
	a.assemble('pong/Pong.asm')
	a.assemble('rect/Rect.asm')
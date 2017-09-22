"""
For assebling the hdl codes without symbols.
"""

from Parser import Parser
from Code import *

def assemble(path, dest=None):
	if not dest:
		dest = path.rsplit('.')[0] + '.hack'
	with open(dest, 'w') as target:
		p = Parser(path)
		while p.has_more_commands():
			p.advance()
			if p.command_type == 'a_command':
				target.write(complete_A(p.symbol) + '\n')
			elif p.command_type == 'c_command':
				target.write(complete_C(p.dest, p.comp, p.jump) + '\n')

if __name__ == '__main__':
	assemble(r'add/Add.asm')
	assemble(r'max/MaxL.asm')
	assemble(r'pong/PongL.asm')
	assemble(r'rect/RectL.asm')
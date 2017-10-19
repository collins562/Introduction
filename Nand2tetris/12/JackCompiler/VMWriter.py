"""The VMWriter module provide class VMWriter for write vm command into a vm
file."""

class VMWriter:
    def __init__(self, outpath):
        if not outpath.endswith('.vm'):
            raise ValueError("Expect a vm file.")
        self._file = open(outpath, 'w')

    def close(self):
        self._file.close()

    def write_command(self, command, arg1=None, arg2=None):
        line = ' '.join(str(e) for e in (command, arg1, arg2) if e is not None)
        self._file.write(line + '\n')

    def write_push(self, seg, index):
        self.write_command('push', seg, index)

    def write_pop(self, seg, index):
        self.write_command('pop', seg, index)

    def write_arithmetic(self, command):
        self.write_command(command)

    def write_label(self, label):
        self.write_command('label', label)

    def write_goto(self, label):
        self.write_command('goto', label)

    def write_if(self, label):
        self.write_command('if-goto', label)

    def write_call(self, name, num_args):
        self.write_command('call', name, num_args)

    def write_function(self, name, num_locals):
        self.write_command('function', name, num_locals)

    def write_return(self):
        self.write_command('return')

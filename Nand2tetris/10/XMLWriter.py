"""The XMLWriter module provide class XMLWriter for write xml structure into a xml
file."""

class XMLWriter:
    token_convert = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}

    def set_filepath(self, outpath):
        if not outpath.endswith('.xml'):
            raise ValueError("Expect a xml file.")
        self._file = open(outpath, 'w')

    def write(self, text):
        self._file.write(text)

    def close(self):
        self._file.close()

    def write_tag(self, tag, end=False, newline=False):
        head = '</' if end else '<'
        tail = '>\n' if newline else '>'
        self.write(head + tag + tail)

    def write_terminal(self, terminal, tok_tag):
        if terminal in self.token_convert:
            terminal = self.token_convert[terminal]
        self.write_tag(tok_tag)
        self.write(' ' + str(terminal) + ' ')
        self.write_tag(tok_tag, end=True, newline=True)

    def write_non_terminal(self, non_terminal, end=False):
        return self.write_tag(non_terminal, end=end, newline=True)

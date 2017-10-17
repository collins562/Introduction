"""
For comparison between two file. Because the Textcomparer.bat in my
system doesn't work.
"""

import os

def compare(path1, path2, module):
	with open(path1, 'r') as f1:
		lines1 = f1.readlines()
	with open(path2, 'r') as f2:
		lines2 = f2.readlines()
	line_count = 0
	while lines1 and lines2:
		line_count += 1
		l1 = lines1.pop(0).strip().replace(' ', '')
		l2 = lines2.pop(0).strip().replace(' ', '')
		if l1 != l2:
			file_info = "module {0}, file {1}".format(module, os.path.basename(path1))
			line_info = "line {0}".format(line_count)
			text_info = "  origin: {0}\n  answer: {1}".format(l1, l2)
			raise ValueError("{0}, {1}:\n{2}".format(file_info, line_info, text_info))
	if lines1 or lines2:
		return False
	return True

def get_xml_files(path):
	files = os.listdir(path)
	return [file for file in files if file.endswith('.xml')]

def test(orig_path):
	orig_files = get_xml_files(orig_path)
	for file in orig_files:
		origin = os.path.join(orig_path, file)
		answer = os.path.join(os.path.join(orig_path, 'Xmlresult'), file)
		try:
			assert compare(origin, answer, orig_path), "%s" %file
		except FileNotFoundError:
			print("--{0} has not been implemented yet--".format(file))

def test_Square():
	test('Square')
	print("Square test ended successfully.\n")

def test_ExpressionLessSquare():
	test('ExpressionLessSquare')
	print("ExpressionLessSquare test ended successfully.\n")

def test_ArrayTest():
	test('ArrayTest')
	print("ArrayTest test ended successfully.\n")

if __name__ == '__main__':
	test_ArrayTest()
	test_ExpressionLessSquare()
	test_Square()
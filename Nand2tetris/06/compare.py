"""
For comparison between two hack file. Because the Textcomparer.bat 
in my system doesn't work.
"""

def compare(path1, path2):
	with open(path1, 'r') as f1:
		lines1 = f1.readlines()
	with open(path2, 'r') as f2:
		lines2 = f2.readlines()
	while lines1 and lines2:
		if lines1.pop(0) != lines2.pop(0):
			return False
	return True

def test():
	assert compare(r'add/Add.hack', r'add/Add_ans.hack')
	assert compare(r'max/MaxL.hack', r'max/MaxL_ans.hack')
	assert compare(r'pong/PongL.hack', r'pong/PongL_ans.hack')
	assert compare(r'rect/RectL.hack', r'rect/RectL_ans.hack')
	assert compare(r'max/Max.hack', r'max/Max_ans.hack')
	assert compare(r'pong/Pong.hack', r'pong/Pong_ans.hack')
	assert compare(r'rect/Rect.hack', r'rect/Rect_ans.hack')
	print('Compare ended successfully.')

if __name__ == '__main__':
	test()
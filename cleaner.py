# clean jack file

def clean(fname):
	f = open(fname, 'r')
	jack_lines = []
	in_comment = False
	for line in f:
		if not line.strip():
			continue

		e_com_loc = end_comment(line)
		# we reached end of a comment block
		if in_comment and e_com_loc != -1:
			stripped_line = line[(e_com_loc + 2) :].strip()
			in_comment = False
			if not stripped_line:
				continue
			jack_lines.append(stripped_line)
			continue


		if in_comment:
			continue

		# check if we have /* */ in same line
		s_com_loc = start_comment(line)
		sl_com_loc = slash_comment(line)

		# we have a slash comment
		if (s_com_loc == -1 and e_com_loc == -1 and sl_com_loc != -1):
			stripped_line = line[0:sl_com_loc].strip()
			if not stripped_line:
				continue
			jack_lines.append(stripped_line)
			continue

		# we have a block comment in the same line
		if (s_com_loc != -1 and e_com_loc!= -1):
			comb_line = line[0:s_com_loc] + line[(e_com_loc + 2):]
			if not comb_line.strip():
				continue
			jack_lines.append(comb_line.strip())
			continue

		# we start a block comment
		if (s_com_loc != -1 and not in_comment):
			stripped_line = line[0:s_com_loc].strip()
			in_comment = True
			if not stripped_line:
				continue
			jack_lines.append(stripped_line)
			
			continue

		# here, then we don't have to deal with comment logic
		jack_lines.append(line.strip())

	f.close()
	return jack_lines


			


def start_comment(line):
	if '/*' in line:
		return line.find('/*')
	return -1

def end_comment(line):
	if '*/' in line:
		return line.find('*/')
	return -1

def slash_comment(line):
	if '//' in line:
		return line.find('//')
	return -1


if __name__ == '__main__':
	clean_cmds = clean('Main.jack')
	for cmd in clean_cmds:
		print(cmd)

# split .jack file into a list of words to categorize




def splitWords(clean_cmds):
	word_list = []
	for command in clean_cmds:

		# check if we have a string constant
		if (hasWord(command)):
			stripped_line = grabStringConstant(command)

			# add the string constant 
			before_split = splitLine(stripped_line['beforeline'])
			if len(before_split) != 0:
				word_list += before_split

			word_list.append((stripped_line['word']))

			stringless_line = stripped_line['afterline']


			# could have multiple string constants
			while (hasWord(stringless_line)):
				stripped_line = grabStringConstant(stringless_line)

				before_split = splitLine(stripped_line['beforeline'])
				if len(before_split) != 0:
					word_list += before_split

				word_list.append(stripped_line['word'])
				stringless_line = stripped_line['afterline']

			# split the rest of the stringless line
			word_list += splitLine(stringless_line)

		else:
			word_list += splitLine(command)

	return word_list

def hasWord(line):
	first_quote = line.find("\"")
	if first_quote < 0:
		return False
	second_quote = line[first_quote + 1 : ].find("\"")
	if second_quote < 0:
		return False
	return True

def grabStringConstant(line):
	first_quote = line.find("\"")
	second_quote = line[(first_quote + 1) : ].find("\"") + first_quote
	line_split = {}
	line_split['word'] = line[first_quote : second_quote + 2]
	line_split['beforeline'] = line[0: first_quote]
	line_split['afterline'] = line[second_quote + 2 : ]
	return line_split


# abc.xy
def splitLine(line):
	symbols = ["{","}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
	line_words = []
	current_token = ""
	for letter in line:
		# we are appending to a token
		if letter not in symbols and letter != " ":
			current_token += letter

		# we have seen a symbol
		elif letter in symbols:

			# append current_token if not empty
			if current_token != "":
				line_words.append(current_token)

			# sset current_token to ""
			current_token = ""

			# add the symbol as a token
			line_words.append(letter)

		# we have whitespace
		elif letter == " ":
			if current_token != "":
				line_words.append(current_token)
			current_token = ""
			continue
	# add what ever token is remaining at the end of the line
	line_words.append(current_token)


	return line_words


if __name__ == '__main__':

	clean_cmds = cleaner.clean('Main.jack')
	word_list = splitWords(clean_cmds)
	for word in word_list:

		print(word)


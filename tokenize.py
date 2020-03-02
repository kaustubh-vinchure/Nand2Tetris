
from lxml import etree

def tokenize(word_list):
	tokens = etree.Element('tokens')
	for word in word_list:
		if word is None:
			continue
		elif len(word) == 0:
			continue
		elif checkStringConstant(word) is not None:
			stringConstant = etree.SubElement(tokens, "stringConstant")
			stringConstant.text = " " + word[1:-1] + " "
		elif checkKeyword(word) is not None:
			keyword = etree.SubElement(tokens, "keyword")
			keyword.text = " " + word + " "
		elif checkSymbol(word) is not None:
			symbol = etree.SubElement(tokens, "symbol")
			symbol.text = " " + word + " "
		elif checkInteger(word) is not None:
			integerConstant = etree.SubElement(tokens, "integerConstant")
			integerConstant.text = " " + word + " "
		elif checkIdentifier(word) is not None:
			identifier = etree.SubElement(tokens, "identifier")
			identifier.text = " " + word + " "
	return tokens



def checkKeyword(word):
	keywords = ["class", "constructor", "function", "method", "field", "static", "var", "int", "char", 
				"boolean", "void", "true", "false", "null" , "this", "let", "do", "if", "else", "while", "return"]
	if word in keywords:
		return word
	else:
		return None


def checkSymbol(word):
	symbols = ["{","}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/", "&", "|", "<", ">", "=", "~"]
	if word in symbols:
		return word 
	else:
		return None

def checkInteger(word):
	try:
		int(word)
		return word 
	except ValueError:
		return None

def checkStringConstant(word):
	if len(word) != 0 and word[0] == "\"" and word[-1] == "\"" and len(word)>1:
		return word
	else:
		return None

def checkIdentifier(word):
	if word is None:
		return None
	if len(word) == 0:
		return None
	else:
		return word




if __name__ == "__main__":
	f_test = open("test.txt", "w")
	words = ['(', "\"hello\"", "static", "=", "1555", "hello"]
	tree = tokenize(words)
	tree_string = etree.tostring(tree, pretty_print = True, encoding = 'utf-8').decode('utf-8')
	f_test.write(tree_string)
	f_test.close()


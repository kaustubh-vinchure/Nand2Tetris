import sys
import os
import splitter
import cleaner
import tokenize
from lxml import etree

class Parser():

	def __init__(self, tokens, fout, className):
		self.__tokens = tokens
		self.__idx = 0
		self.__file = fout
		self.__program = etree.Element("class")
		self.__className = className
		self.__numTokens = len(tokens)


	def getTree(self):
		return self.__program
	def writeToFile(self):
		class_string = etree.tostring(self.__program, pretty_print = True, encoding = 'utf-8').decode('utf-8')
		self.__file.write(class_string)
		return

	def isType(self, token_text):
		types = ['int', 'char', 'boolean', self.__className]
		isType = False
		for tp in types:
			if tp in token_text:
				isType = True
				return isType
		return isType

	def next_token(self):
		token = self.__tokens[self.__idx]
		self.__idx += 1
		return token 

	def go_back_one(self):
		self.__idx -= 1

	def createClass(self):
		
		class_key = etree.SubElement(self.__program, "keyword")
		class_key.text = self.next_token().text

		class_name = etree.SubElement(self.__program, "identifier")
		class_name.text = self.next_token().text

		class_start = etree.SubElement(self.__program, "symbol")
		class_start.text = self.next_token().text

		# start class var declaration
		self.createClassVarDec()


		# start subroutine declrations
		self.createSubRoutine()




	def createSubRoutine(self):
		function_types = ['constructor', 'method', 'function']
		while True:

			# check if were done
			first_var = self.next_token()
			if first_var.text.strip() not in function_types:
				self.go_back_one()
				return
			self.go_back_one()

			# we are starting a subroutine declaration
			subroutine = etree.SubElement(self.__program, "subroutineDec")

			# add function type
			ftype = etree.SubElement(subroutine, "keyword")
			ftype.text = self.next_token().text

			# add functionr return type
			ret_type = etree.SubElement(subroutine, "keyword")
			ret_type.text = self.next_token().text
			if (ret_type.text.strip() == self.__className):
				ret_type.tag = "identifier"


			# add subroutine name
			f_name = etree.SubElement(subroutine, "identifier")
			f_name.text = self.next_token().text

			# add parenthesis
			start_param = etree.SubElement(subroutine, "symbol")
			start_param.text = self.next_token().text

			# create paramlist
			param_list = etree.SubElement(subroutine, "parameterList")
			self.createParamList(param_list)

			# add terminating paramlist
			end_param = etree.SubElement(subroutine, "symbol")
			end_param.text = self.next_token().text

			# add subpourtine body
			subroutineBody = etree.SubElement(subroutine, "subroutineBody")

			# add start bracket
			start_body = etree.SubElement(subroutineBody, "symbol")
			start_body.text = self.next_token().text


			# add varDeclarations
			self.createVarDecs(subroutineBody)

			# add statements
			statements = etree.SubElement(subroutineBody, "statements")
			self.createStatements(statements)

			# add semicol
			end_body = etree.SubElement(subroutineBody, "symbol")
			end_body.text = self.next_token().text


	def createVarDecs(self, subroutineBody):
		while True:

			var_dec = self.next_token() 

			# we are not declaring a variable
			if (var_dec.text.strip() != 'var'):
				self.go_back_one()
				return 

			# create varDec
			new_var_dec = etree.SubElement(subroutineBody, "varDec")

			# add 'var'
			var_n = etree.SubElement(new_var_dec, "keyword")
			var_n.text = var_dec.text


			# add type
			var_t = etree.SubElement(new_var_dec, "keyword")
			var_t.text = self.next_token().text
			if (var_t.text.strip() == self.__className):
				var_t.tag = "identifier"

			# add name
			var_name = etree.SubElement(new_var_dec, "identifier")
			var_name.text = self.next_token().text

			# check if there is a comma and add more otherwise
			while True:
				term = self.next_token()
				if (term.text.strip() == ';'):
					self.go_back_one()
					break

				# add comma
				var_com = etree.SubElement(new_var_dec, "symbol")
				var_com.text = term.text

				# add name
				var_name = etree.SubElement(new_var_dec, "identifier")
				var_name.text = self.next_token().text

			# add semicolon
			var_end = etree.SubElement(new_var_dec, "symbol")
			var_end.text = self.next_token().text


	def createLetStatement(self, statement):
		# assume we are creating a let statement

		let_term = etree.SubElement(statement, "keyword")
		let_term.text = self.next_token().text


		# add varName
		let_varname = etree.SubElement(statement, "identifier")
		let_varname.text = self.next_token().text

		# check if we have array indexing

		if (self.next_token().text.strip() == '['):
			self.go_back_one()
			start_index = etree.SubElement(statement, "symbol")
			start_index.text = self.next_token().text

			expression_idx = etree.SubElement(statement, "expression")
			self.createExpression(expression_idx)

			end_index = etree.SubElement(statement, "symbol")
			end_index.text = self.next_token().text 

		else:
			self.go_back_one()
		
		# add equal sign 
		equal_sign = etree.SubElement(statement, "symbol")
		equal_sign.text = self.next_token().text

		#create expression
		expression_state = etree.SubElement(statement, "expression")
		self.createExpression(expression_state)

		# add semicolon
		semi = etree.SubElement(statement, "symbol")
		semi.text = self.next_token().text 

		return


	def createDoStatement(self, statement):
		# add 'do'
		do_t = etree.SubElement(statement, "keyword")
		do_t.text = self.next_token().text 

		# add subroutine call
		self.createSubroutineCall(statement)

		# add semicolon
		end_st = etree.SubElement(statement, "symbol")
		end_st.text = self.next_token().text

		return 

	def createWhileStatement(self, statement):
		# add while
		while_t = etree.SubElement(statement, "keyword")
		while_t.text = self.next_token().text 

		#add parenthesis
		st_exp = etree.SubElement(statement, "symbol")
		st_exp.text = self.next_token().text 

		# add expression
		self.createExpression(statement)

		#add pa
		en_exp = etree.SubElement(statement, "symbol")
		en_exp.text = self.next_token().text

		# add curly brace
		st_cur = etree.SubElement(statement, "symbol")
		st_cur.text = self.next_token().text 

		# add statements
		self.createStatements(statement)

		#add curly brace
		en_cur = etree.SubElement(statement, "symbol")
		en_cur.text = self.next_token().text

		return

	def createIfStatement(self, statement):
		# add if
		if_t = etree.SubElement(statement, "keyword")
		if_t.text = self.next_token().text 

		# add open parent
		st_ch = etree.SubElement(statement, "symbol")
		st_ch.text = self.next_token().text

		# add expression
		if_exp = etree.SubElement(statement, "expression")
		self.createExpression(if_exp)

		# add close paren
		cl_ch = etree.SubElement(statement, "symbol")
		cl_ch.text = self.next_token().text

		# add curly
		st_cr = etree.SubElement(statement, "symbol")
		st_cr.text = self.next_token().text 

		#add statements
		if_states = etree.SubElement(statement, "statements")
		self.createStatements(if_states)

		# add close curly
		cl_cr = etree.SubElement(statement, "symbol")
		cl_cr.text = self.next_token().text

		# check else
		maybe_else = self.next_token()
		if (maybe_else.text.strip() == 'else'):

			# add else
			else_t = etree.SubElement(statement, 'keyword')
			else_t.text = maybe_else.text

			# add curly brace
			e_cr_s = etree.SubElement(statement, 'symbol')
			e_cr_s.text = self.next_token().text

			# add statements
			else_statements = etree.SubElement(statement, 'statements')
			self.createStatements(else_statements)

			# add curly brace
			e_cr_e = etree.SubElement(statement, "symbol")
			e_cr_e.text = self.next_token().text
		else:
			self.go_back_one()

		return 





	def createSubroutineCall(self, statement):
		# add identifier
		call_first = etree.SubElement(statement, "identifier")
		call_first.text = self.next_token().text

		# check if next one is a period

		if (self.next_token().text.strip() == '.'):
			self.go_back_one()

			# add period
			per = etree.SubElement(statement, "symbol")
			per.text = self.next_token().text

			# add func name
			fun_name = etree.SubElement(statement, "identifier")
			fun_name.text = self.next_token().text 

		else:
			self.go_back_one()

		# add paren
		st_exp = etree.SubElement(statement, "symbol")
		st_exp.text = self.next_token().text 

		# create expression list
		exp_list = etree.SubElement(statement, "expressionList")
		self.createExpressionList(exp_list)

		# end paren
		en_exp = etree.SubElement(statement, "symbol")
		en_exp.text = self.next_token().text 

		return 



	def createTerm(self, expression):


		term_token = self.next_token()

		# check if we have a constant
		if (term_token.text.strip() == 'true' or term_token.text.strip() == 'false' or 'Constant' in term_token.tag.strip()):

			term = etree.SubElement(expression, term_token.tag)
			term.text = term_token.text
			return

		# check if we have a varname
		if (term_token.tag.strip() == 'identifier'):

			#check if next term is a parenthesis or a period (subroutine call)
			check_token = self.next_token().text
			if (check_token.strip() == '(' or check_token.strip() == '.'):
				self.go_back_one()
				self.go_back_one()

				#add subroutineCall
				self.createSubroutineCall(expression)
				return 

			else:
				self.go_back_one()

			term = etree.SubElement(expression, "identifier")
			term.text = term_token.text

			# check if the enxt term in a bracket (index)
			if self.next_token().text.strip() == '[':
				self.go_back_one()
				start_exp = etree.SubElement(expression, "symbol")
				start_exp.text = self.next_token().text
				# create expression in bracket

				nested_exp = etree.SubElement(expression, "expression")
				self.createExpression(nested_exp)

				 # add end bracket
				end_exp = etree.SubElement(expression, "symbol")
				end_exp.text = self.next_token().text
				return

			else:
				self.go_back_one()

			return

		# check if we have unary operator then term
		if term_token.text.strip() == '-' or term_token.text.strip() == '~':
			# add unary operator
			unary_op = etree.SubElement(expression, "keyword")
			unary_op.text = term_token.text

			# create term
			unary_exp = etree.SubElement(expression, "expression")
			self.createExpression(unary_exp)

			return

		if term_token.tag.strip() == 'keyword':
			term = etree.SubElement(expression, "keyword")
			term.text = term_token.text 
			return
		return

	def createReturnStatement(self, retStatement):

		# add return word
		ret_key = etree.SubElement(retStatement, "keyword")
		ret_key.text = self.next_token().text

		# check if we're done
		term = self.next_token()
		self.go_back_one()

		if (term.text.strip() == ';'):
			end_ret = etree.SubElement(retStatement, "symbol")
			end_ret.text = self.next_token().text

			return 

		# add expressioon

		exp = etree.SubElement(retStatement, "expression")
		self.createExpression(exp)

		# add semi
		end_ret = etree.SubElement(retStatement, "symbol")
		end_ret.text = self.next_token().text


	def createExpressionList(self, expList):
		while True:
			if (self.next_token().text.strip() == ')'):
				self.go_back_one()
				return

			else:
				self.go_back_one()

			# add expression
			exp = etree.SubElement(expList, "expression")
			self.createExpression(exp)

			# check if we have a comma
			if (self.next_token().text == ','):
				self.go_back_one()

				com = etree.SubElement(expList, "symbol")
				com.text = self.next_token().text 
			else:
				self.go_back_one()
		return



	def createExpression(self, expression):

		op = ['+', '-', '*', '/', '&', '|' , '<', '>', '=']
		# create term
		exp_term = etree.SubElement(expression, "term")
		self.createTerm(exp_term)

		while True:

			# check if we have an operator
			op_token = self.next_token()
			if (op_token.text.strip() in op):
				operator = etree.SubElement(expression, "symbol")
				operator.text = op_token.text
			else:
				self.go_back_one()
				return

			# add next term 
			next_term = etree.SubElement(expression, "term")
			self.createTerm(next_term)

		return


		


	def createStatements(self, statements):
		# iterate over statements and look for 
		while True:
			# peek a ahead to see type of sttatemtn
			statement_type = self.next_token().text.strip()
			self.go_back_one()

			# check if let statement
			if (statement_type == 'let'):
				letStatement = etree.SubElement(statements, "letStatement")
				self.createLetStatement(letStatement)

			elif (statement_type == 'while'):
				whileStatement = etree.SubElement(statements, "whileStatement")
				self.createWhileStatement(whileStatement)
				continue

			elif (statement_type == 'do'):
				doStatement = etree.SubElement(statements, "doStatement")
				self.createDoStatement(doStatement)

			elif (statement_type == 'return'):
				returnStatement = etree.SubElement(statements, "returnStatement")
				self.createReturnStatement(returnStatement)
				continue

			elif (statement_type == 'if'):
				ifStatement = etree.SubElement(statements, "ifStatement")
				self.createIfStatement(ifStatement)

			else:
				return






	def createParamList(self, paramList):
		# check if empty param list
		end_param = self.next_token()
		if (end_param.text.strip() == ')'):
			self.go_back_one()
			return

		self.go_back_one()

		while True:

			# add param type
			var_type = etree.SubElement(paramList, "keyword")
			var_type_t = self.next_token()
			if (var_type_t.text.strip() == self.__className):
				var_type.tag = "identifier"
			var_type.text = var_type_t.text 

			# add param name
			var_name = etree.SubElement(paramList, "identifier")
			var_name.text = self.next_token().text 

			# check if we reached the end 
			terminate = self.next_token()
			# we reached end
			if (terminate.text.strip() == ')'):
				self.go_back_one()
				return

			# add comma otherwise and keep going
			com = etree.SubElement(paramList, "symbol")
			com.text = terminate.text







	def createVarList(self, classVarDec):
		while True:
			var = etree.SubElement(classVarDec, "identifier")
			var.text = self.next_token().text

			if (self.next_token().text.strip()== ';'):
				self.go_back_one()
				var_end = etree.SubElement(classVarDec, "symbol")
				var_end.text = self.next_token().text
				return

			# add comma
			var_split = etree.SubElement(classVarDec, "symbol")
			var_split.text = self.next_token().text


	def createClassVarDec(self):

		first_var = self.next_token()
		# no class variable declaration
		if 'static' not in first_var.text and 'field' not in first_var.text:
			self.go_back_one()
			return

		# we have class variable declarations
		self.go_back_one()
		while True:
			# check if we're done
			first_var = self.next_token()
			if ('static' not in first_var.text and 'field' not in first_var.text):
				self.go_back_one()
				return
			self.go_back_one()
			classVarDec = etree.SubElement(self.__program, "classVarDec")

			vis = etree.SubElement(classVarDec, "keyword")
			vis.text = self.next_token().text

			tp_token = self.next_token().text

			if tp_token.strip() == self.__className:
				tp = etree.SubElement(classVarDec, "identifier")
				tp.text = tp_token
			else:
				tp = etree.SubElement(classVarDec, "keyword")
				tp.text = tp_token


			varName = etree.SubElement(classVarDec, "identifier")
			varName.text = self.next_token().text

			# if there are multiple vars:
			terminate = self.next_token()
			if (terminate.text == ' , '):
				split_var = etree.SubElement(classVarDec, "symbol")
				split_var.text = ' , '
				self.createVarList(classVarDec)
			else:
				# we have semicolon
				end_var = etree.SubElement(classVarDec, "symbol")
				end_var.text = terminate.text 

















	




if __name__ == '__main__':
	fdir = sys.argv[1]
	for file in os.listdir(fdir):
		f_name, f_ext = os.path.splitext(file)
		if (f_ext == '.jack'):
			f_full = os.path.join(fdir, file)
			f_clean = cleaner.clean(f_full)
			f_split = splitter.splitWords(f_clean)
			f_save = os.path.join(fdir, f_name)
			f_savet = f_save
			f_save += '.xml'
			f_save_f = open(f_save, 'w')

			f_savet += 'T' + '.xml'
			f_savet_f = open(f_savet, 'w')
			f_tokens = tokenize.tokenize(f_split)

			token_string = etree.tostring(f_tokens, pretty_print = True, encoding = 'utf-8').decode('utf-8')
			f_savet_f.write(token_string)
			f_savet_f.close()


			f_parser = Parser(f_tokens, f_save_f, f_name)

			f_parser.createClass()

			parse_tree = f_parser.getTree()
			
			print(len(parse_tree.findall('subroutineDec')))

			f_parser.writeToFile()

			f_save_f.close()


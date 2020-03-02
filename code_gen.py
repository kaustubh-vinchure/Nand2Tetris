import symbolizer
import splitter
import cleaner
import tokenize
from lxml import etree
import sys
import os




class Generator():
	

	def __init__(self, program, symbol_table, class_name):
		self.__program = program
		self.__symbol_table = symbol_table
		self.__vm_commands = []	
		self.__if_count = 0
		self.__while_count = 0
		self.__class_name = class_name
		self.__num_fields = 0

		return

	def returnVMCommands(self):
		return self.__vm_commands
	def writePush(self, segment, index):
		vm_command = 'push' + ' ' + segment + ' ' + str(index)
		self.__vm_commands.append(vm_command)
		return

	def writePop(self, segment, index):
		vm_command = 'pop' + ' ' + segment + ' ' + str(index)
		self.__vm_commands.append(vm_command)
		return 

	def writeArithmetic(self, command):
		vm_command = command
		self.__vm_commands.append(vm_command)
		return 

	def writeLabel(self, label):
		vm_command = 'label' + ' ' + label
		self.__vm_commands.append(vm_command)
		return 

	def writeGoto(self, label):
		vm_command = 'goto' + ' ' + label
		self.__vm_commands.append(vm_command)
		return 

	def writeIf(self, label):
		vm_command = 'if-goto' + ' ' + label
		self.__vm_commands.append(vm_command)
		return 

	def writeCall(self, f_name, nArgs):
		# print(f_name)
		vm_command = 'call' + ' ' + f_name + ' ' + str(nArgs)
		self.__vm_commands.append(vm_command)
		return 

	def writeFunction(self, f_name, nLocals):
		vm_command = 'function' + ' ' + self.__class_name+'.'+f_name + ' ' + str(nLocals)
		self.__vm_commands.append(vm_command)
		return 

	def writeReturn(self):
		vm_command = 'return'
		self.__vm_commands.append(vm_command)
		return 

	def getSymIdx(self, scope_name):
		sym_idx = 0
		for entry in self.__symbol_table:
			if self.__symbol_table[sym_idx]['scope'] == scope_name:
				return sym_idx
			sym_idx += 1
		return None
	def parseSymbolTable(self, sym_idx, identifier):
		curr_table = self.__symbol_table[sym_idx]
		for var in curr_table['symbols']:
			if var['name'] == identifier.strip():
				var_name = var['kind'] + ' ' + str(var['num'])
				return var_name

		# check if class variable
		for var in self.__symbol_table[0]['symbols']:
			if var['name'] == identifier.strip():
				var_name = var['kind'] + ' ' + str(var['num'])
				if (var['kind'] == 'field'):
					var_name = 'this' + ' ' + str(var['num'])
					return var_name
				return var_name
		return None

	def getSymbolType(self, sym_idx, identifier):
		curr_table = self.__symbol_table[sym_idx]
		for var in curr_table['symbols']:
			if var['name'] == identifier.strip():
				var_type = var['type']
				return var_type

		# check class varialibe
		for var in self.__symbol_table[0]['symbols']:
			if var['name'] == identifier.strip():
				var_type = var['type']
				return var_type

		return None
	def compileExpressionList(self, expList, sym_idx):
		expressions = expList.findall('expression')
		nExp = 0
		for expression in expressions:
			self.compileExpression(expression, sym_idx)
			nExp += 1

		return nExp

	def compileClass(self):

		# add class variable declarations
		self.compileClassVarDec()

		# iterate over each subroutine declaration and write those
		subroutineDecs = self.__program.findall('subroutineDec')


		for subroutineDec in subroutineDecs:
			self.declareSubroutine(subroutineDec)

		return


	def declareSubroutine(self, subroutineDec):
		subroutineElements = subroutineDec.getchildren()
		subroutineType = subroutineElements[0].text.strip()
		subroutineName = subroutineElements[2].text.strip()
		subroutineBody = subroutineElements[-1]
		sym_idx = self.getSymIdx(subroutineName)
		# write function subroutineName nLocal
		self.declareSubroutineName(subroutineName, sym_idx, subroutineType)

		# compile body
		self.compileSubroutineBody(subroutineBody, sym_idx)




		return

	def compileSubroutineBody(self, subroutineBody, sym_idx):
		statements = subroutineBody.find('statements')
		self.compileStatements(statements, sym_idx)
		return

	def compileStatements(self,statements, sym_idx):
		statement_list = statements.getchildren()
		for statement in statement_list:
			statement_type = statement.tag.strip()
			if statement_type == 'doStatement':
				self.compileDoStatement(statement, sym_idx)
			elif statement_type == 'letStatement':
				self.compileLetStatement(statement, sym_idx)
			elif statement_type == 'ifStatement':
				self.compileIfStatement(statement, sym_idx)
			elif statement_type == 'whileStatement':
				self.compileWhileStatement(statement, sym_idx)
			elif statement_type == 'returnStatement':
				self.compileReturnStatement(statement, sym_idx)
			else:
				pass

		return


	# if ( expression ) { statements } "'else' { statements } ""
	def compileIfStatement(self, ifStatement, sym_idx):
		if_components = ifStatement.getchildren()
		if_exp = if_components[2]
		if_statement1 = if_components[5]
		if_statement2 = if_statement1

		has_else = len(if_components) > 7
		if has_else:
			if_statement2 = if_components[9]

		L1 = 'if_La'+str(self.__if_count)
		L2 = 'if_Lb'+str(self.__if_count)
		self.__if_count += 1

		self.compileExpression(if_exp, sym_idx)
		self.writeArithmetic('not')

		self.writeIf(L1)
		self.compileStatements(if_statement1, sym_idx)

		self.writeGoto(L2)
		self.writeLabel(L1)
		if has_else:
			self.compileStatements(if_statement2, sym_idx)
		self.writeLabel(L2)

		return

	# while ( expression ) { statements }
	def compileWhileStatement(self, whileStatement, sym_idx):
		while_components = whileStatement.getchildren()
		while_exp = while_components[2]
		while_statements = while_components[5]


		L1 = 'while_La'+str(self.__while_count)
		L2 = 'while_Lb' + str(self.__while_count)
		self.__while_count += 1

		self.writeLabel(L1)
		self.compileExpression(while_exp, sym_idx)
		self.writeArithmetic('not')
		self.writeIf(L2)
		self.compileStatements(while_statements, sym_idx)
		self.writeGoto(L1)
		self.writeLabel(L2)

		return

	# do subroutineCall ;
	def compileDoStatement(self, doStatement, sym_idx):

		do_components = doStatement.getchildren()
		call_elements = do_components[1:-1]
		fname = call_elements[0].text.strip()
		expList = call_elements[2]
		nArgs = 0
		# check if objName.funcName(expList)
		if call_elements[1].text.strip() == '.':
			expList = call_elements[4]
			# push objName if obj
			objNameVar = self.parseSymbolTable(sym_idx, call_elements[0].text.strip())
			
			# it is an object
			if objNameVar is not None:
				objNameVarSplit = objNameVar.split()
				self.writePush(objNameVarSplit[0], int(objNameVarSplit[1]))
				objType = self.getSymbolType(sym_idx, call_elements[0].text.strip())
				fname = call_elements[2].text.strip()
				# if (objType is None):
				# 	print(objNameVarSplit[0])
				if (objType != None):
					fname = objType + '.' + call_elements[2].text.strip()
				nArgs += 1

			# it is the class name
			else:
				fname = call_elements[0].text.strip() + '.' + call_elements[2].text.strip()
		#call is from funcName(expList)
		else:
			nArgs += 1
			fname = self.__class_name + '.' + call_elements[0].text.strip()
			self.writePush('pointer', 0)

		# fname is set properly and we have expList element
		num_args = self.compileExpressionList(expList, sym_idx)
		nArgs += num_args


		# write call to function
		self.writeCall(fname, nArgs)

		self.writePop('temp', 0)

		return


	# return expression
	def compileReturnStatement(self, retStatement, sym_idx):
		ret_components = retStatement.getchildren()
		has_exp = len(ret_components) > 2

		if has_exp:
			ret_exp = ret_components[1]
			self.compileExpression(ret_exp, sym_idx)
		else:
			self.writePush('constant', 0)

		self.writeReturn()

		return

	# let varName ([expression])? = expression ;
	def compileLetStatement(self, letStatement, sym_idx):
		let_components = letStatement.getchildren()
		is_array = len(let_components) > 5
		dest_var = self.parseSymbolTable(sym_idx, let_components[1].text.strip())
		if dest_var is None:
			print('error in let', let_components[1].text.strip())
		dest_split = dest_var.split()

		# check if array
		if is_array:
			arr_exp = let_components[3]
			self.compileExpression(arr_exp,sym_idx)

			self.writePush(dest_split[0], int(dest_split[1]))
			self.writeArithmetic('add')
			self.writePop('temp', 1)

			eval_exp = let_components[6]
			self.compileExpression(eval_exp, sym_idx)

			self.writePush('temp', 1)
			self.writePop('pointer', 1)
			self.writePop('that', 0)

		else:
			eval_exp = let_components[3]
			self.compileExpression(eval_exp, sym_idx)

			self.writePop(dest_split[0], int(dest_split[1]))

		return





	def declareSubroutineName(self, subroutineName, sym_idx, subroutineType):
		nLocal = 0
		for sym in self.__symbol_table[sym_idx]['symbols']:
			if sym['kind'] == 'local':
				nLocal += 1

		self.writeFunction(subroutineName, nLocal)
		if subroutineType == 'constructor':
			self.writePush('constant', self.__num_fields)
			self.writeCall('Memory.alloc', 1)
			self.writePop('pointer', 0)

		elif subroutineType == 'method':
			self.writePush('argument', 0)
			self.writePop('pointer', 0)

		return


	# symbol table already contains all the class variables
	def compileClassVarDec(self):
		class_sym_idx = self.getSymIdx('class')
		class_sym = self.__symbol_table[class_sym_idx]
		for var in class_sym['symbols']:
			var_kind = var['kind']
			if var_kind == 'field':
				self.__num_fields += 1
				var_kind = 'this'

			var_num = var['num']

			# push var
			self.writePush(var_kind, int(var_num))




	# term op term op term ... 
	def compileExpression(self, expression, sym_idx):
		op_terms = {'+' : 'add',
			   '-' : 'sub',
			   '*' : 'call Math.multiply 2',
			   '/' : 'call Math.divide 2', 
			   '&' : 'and',
			   '|' : 'or', 
			   '>' : 'gt',
			   '<' : 'lt',
			   '=' : 'eq'}
		terms = expression.findall('term')
		ops = expression.findall('symbol')
		ops += expression.findall('keyword')

		# compile first term
		self.compileTerm(terms[0], sym_idx)

		i = 1

		while i < len(terms):
			# compile term
			self.compileTerm(terms[i], sym_idx)

			# add operation
			self.writeArithmetic(op_terms[ops[i-1].text.strip()])

			i += 1

		return


	def compileSubroutineCall(self, subroutineCall, sym_idx):
		call_elements = subroutineCall.getchildren()
		fname = call_elements[0].text.strip()
		expList = call_elements[2]
		nArgs = 0
		# check if objName.funcName(expList)
		if call_elements[1].text.strip() == '.':
			expList = call_elements[4]
			# push objName if obj
			objNameVar = self.parseSymbolTable(sym_idx, call_elements[0].text.strip())
			
			# it is an object
			if objNameVar is not None:
				objNameVarSplit = objNameVar.split()
				self.writePush(objNameVarSplit[0], int(objNameVarSplit[1]))
				objType = self.getSymbolType(sym_idx, call_elements[0].text.strip())
				fname = objType + '.' + call_elements[2].text.strip()
				nArgs += 1

			# it is the class name
			else:
				fname = call_elements[0].text.strip() + '.' + call_elements[2].text.strip()
		#call is from funcName(expList)
		else:
			nArgs += 1
			fname = self.__class_name + '.' + call_elements[0].text.strip()
			self.writePush('pointer', 0)

		# fname is set properly and we have expList element
		num_args = self.compileExpressionList(expList, sym_idx)
		nArgs += num_args


		# write call to function
		self.writeCall(fname, nArgs)

		return

	def compileTerm(self, term, sym_idx):
		keywords = {'false' : 0, 'null' : 0, 'true' : -1, 'this' : 0}
		unaryOp = {'~': 'not', '-' : 'neg'}
		term_children = term.getchildren()
		if len(term_children) == 1:
			single_term = term_children[0]
		# handle integerConstant
			try:
				int_term = int(single_term.text.strip())
				isNegative = False
				if int_term < 0:
					int_term = abs(int_term)
					isNegative = True
				self.writePush('constant', int_term)
				if isNegative:
					self.writeArithmetic('neg')
				return
			except ValueError:
				pass
		# handle stringConstant
			if single_term.tag.strip() == 'stringConstant':
				string_constant = single_term.text.strip()
				self.writePush('constant', len(string_constant))
				self.writeCall('String.new', 1)
				for letter in string_constant:
					char_ascii = ord(letter)
					self.writePush('constant', char_ascii)
					self.writeCall('String.appendChar', 2)
				return

		# handle keywordContant (true, false, null)
			if single_term.text.strip() in keywords.keys():
				key_term = keywords[single_term.text.strip()]
				if single_term.text.strip() == 'this':
					self.writePush('pointer', 0)
				else:
					isNegative = False
					if key_term < 0:
						key_term = abs(key_term)
						isNegative = True
					self.writePush('constant', key_term)
					if isNegative:
						self.writeArithmetic('neg')
				return
		# handle varName
			var_parsed = self.parseSymbolTable(sym_idx, single_term.text.strip())
			if var_parsed != None:
				var_split = var_parsed.split()
				self.writePush(var_split[0], int(var_split[1]))
				return

			print('error in compileTerm', single_term.text.strip())

		# handle unaryOp term
		if len(term_children) == 2 and term_children[0].text.strip() in unaryOp.keys():
			self.compileTerm(term_children[1], sym_idx) # term
			self.writeArithmetic(unaryOp[term_children[0].text.strip()])
			return

		# handle (expression) 
		if len(term_children) == 3 and term_children[0].text.strip() == '(':
			self.compileExpression(term_children[1], sym_idx) #'(' 'expression' ')'
			return
		# handle varName['expression']
		if len(term_children) == 4 and term_children[1].text.strip() == '[':
			self.compileExpression(term_children[2], sym_idx)

			# load array
			arr_var = self.parseSymbolTable(sym_idx, term_children[0].text.strip())
			if arr_var is None:
				print('error with array', term.text.strip())
				return
			arr_split = arr_var.split()

			# push arr loc
			self.writePush(arr_split[0], int(arr_split[1]))

			self.writeArithmetic('add')

			self.writePop('pointer', 1)

			self.writePush('that', 0)

			return
		# handle subroutineCall
		# print("subCall")
		# for children in term_children:
		# 	print(children.tag)
		if len(term) == 0:
			print(term.tag)
		self.compileSubroutineCall(term, sym_idx)


if __name__ == '__main__':
	fdir = sys.argv[1]
	#f_symbols = []

	for file in os.listdir(fdir):
		f_name, f_ext = os.path.splitext(file)
		if (f_ext == '.jack'):
			f_full = os.path.join(fdir, file)
			f_clean = cleaner.clean(f_full)
			f_split = splitter.splitWords(f_clean)
			f_save = os.path.join(fdir, f_name)
			f_save += '.vm'
			f_save_f = open(f_save, 'w')
			f_parse_out =  'test/' + f_name + '.xml'
			f_test_f = open(f_parse_out, 'w')
			f_tokens = tokenize.tokenize(f_split)


			f_parser = symbolizer.Parser(f_tokens, f_save_f, f_name)

			f_parser.createClass()

			parse_tree = f_parser.getTree()

			parse_string = etree.tostring(parse_tree, pretty_print = True, encoding = 'utf-8').decode('utf-8')
			f_test_f.write(parse_string)			

			f_test_f.close()
			sym = symbolizer.Symbolizer(parse_tree)

			sym.symbolize()

			f_symbols = sym.get_symbol_table()


			gen = Generator(parse_tree, f_symbols, f_name)

			gen.compileClass()

			vm_commands = gen.returnVMCommands()

			for comm in vm_commands:
				f_save_f.write(comm)
				f_save_f.write("\n")

			f_save_f.close()








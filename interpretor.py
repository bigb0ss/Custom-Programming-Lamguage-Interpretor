from sys import *

import re


def check(string):
	try:
		result = re.match(r'\$[a-z]([a-z]|[0-9])*',string)
		if result.group(0) ==string:
			return True
		else:
			return False
	except:
		pass

tokens=[]
num_stack=[]
symbols={}

def open_file(filename):
	data=open(filename,"r").read()
	data += "<EOF>"
	return data

def lex(filecontents):
	tok=""
	state=0
	string=""
	expr=""
	var=""
	varstarted=0
	isexpr=0
	filecontents = list(filecontents)
	for char in filecontents:
		tok+=char
		if tok==" ":
			if state==0:
				tok=""
			else:
				tok=" "
		elif tok=="\n" or tok=="<EOF>":
			if expr!="" and isexpr==1:
				tokens.append("EXPR:"+expr)
				expr=""
			elif expr!="" and isexpr==0:
				tokens.append("NUM:"+expr)
				expr=""
			elif var!="":
				tokens.append("VAR:"+var)
				var=""
				varstarted=0
			tok=""
		elif tok=="=" and state==0:
			if expr!="" and isexpr==0:
				tokens.append("NUM:"+expr)
				expr=""
			if var!="" and check(var):
				tokens.append("VAR:"+var)
				var=""
				varstarted=0
			if tokens[-1]=="EQUALS":
				tokens[-1]="EQEQ"
			else:
				tokens.append("EQUALS")
			tok=""
		elif tok=='$' and state==0:
			varstarted=1
			var+=tok
			tok=""
		elif varstarted==1:
			if tok=="<" or tok==">":
				if var!="":
					tokens.append("VAR:"+var)
					var=""
					varstarted=0
			var+=tok
			tok = ""
		elif tok=="DISPLAY" or tok=="paathuko":
			tokens.append("PRINT")
			tok=""
		elif tok=="ENDIF" or tok=="endif":
			tokens.append("ENDIF")
			tok=""
		
		elif tok=="IF" or tok=="if":
			tokens.append("IF")
			tok=""
		elif tok=="THEN" or tok=="then":
			if expr!="" and isexpr==0:
				tokens.append("NUM:"+expr)
				expr=""
			tokens.append("THEN")
			tok=""
		elif tok=="INPUT" or tok=="input":
			tokens.append("INPUT")
			tok=""
		elif tok=="0" or tok=="1" or tok=="2" or tok=="2" or tok=="3" or tok=="4" or tok=="5" or tok=="6" or tok=="7" or tok=="8" or tok=="9":
			expr+=tok
			tok=""
		elif tok=="+" or tok=="-" or tok=="(" or tok==")" or tok=="%" or tok=="*" or tok=="/":
			isexpr=1
			expr+=tok
			tok=""
		elif tok=="\t":
			tok=""
		elif tok=="\"" or tok==" \"":
			if state==0:
				state=1
			elif state==1:
				tokens.append("STRING:"+string)
				string=""
				state=0
				tok=""
		elif state==1:
			string+=tok
			tok=""

	return tokens

def evaluate(express):
	return eval(express)

def assign(name,value):
	symbols[name[4:]]=value

def getValue(name):
	if name in symbols:
		return symbols[name]
	else:
		return "VARIABLE ERROR : Undefined Variable Found"
		exit()

def printer(value):
	if value[:6]=="STRING":
		print(value[8:])
	elif value[:3]=="NUM":
		print(value[4:])
	elif value[:4]=="EXPR":
		print(evaluate(value[5:]))

def getInput(string, variable):
	x = input(string+" ")
	x = "\""+x
	symbols[variable]="STRING:"+x

def find_end(i,toks,check):
	for i in range(i,len(toks)):
		if toks[i]==check:
			return i
	print("ERROR : If statement not closed")
	exit()

def parser(toks):
	i=0
	while(i < len(toks)):
		if toks[i]=="ENDIF":
			i+=1
		elif toks[i] + " " + toks[i+1][0:6] == "PRINT STRING" or toks[i] + " " +toks[i+1][0:3]=="PRINT NUM"or toks[i] + " " +toks[i+1][0:3]=="PRINT VAR" or toks[i] + " " +toks[i+1][0:4]=="PRINT EXPR":
			if toks[i+1][0:6]=="STRING":
				printer(toks[i+1])
			elif toks[i+1][0:3]=="NUM":
				printer(toks[i+1])
			elif toks[i+1][0:4]=="EXPR":
				printer(toks[i+1])
			elif toks[i+1][:3]=="VAR":
				printer(getValue(toks[i+1][4:]))

			i+=2
		
		elif toks[i][:3] +" "+ toks[i+1]+" "+toks[i+2][0:6]=="VAR EQUALS STRING" or toks[i][:3] +" "+ toks[i+1]+" "+toks[i+2][0:3]=="VAR EQUALS NUM"or toks[i][:3] +" "+ toks[i+1]+" "+toks[i+2][0:3]=="VAR EQUALS VAR" or toks[i][:3] +" "+ toks[i+1]+" "+toks[i+2][0:4]=="VAR EQUALS EXPR":
			if toks[i+2][:6]=="STRING":
				assign(toks[i],toks[i+2])
			elif toks[i+2][:3]=="NUM":
				assign(toks[i],toks[i+2])
			elif toks[i+2][:4]=="EXPR":
				assign(toks[i],"NUM:"+str(evaluate(toks[i+2][5:])))
			elif toks[i+2][:3]=="VAR":
				assign(toks[i],getValue(toks[i+2][4:]))
			i+=3
		
		elif toks[i] +" "+ toks[i+1][:6] +" "+ toks[i+2][:3] =="INPUT STRING VAR":
			getInput(toks[i+1][8:],toks[i+2][4:])
			i+=3
		elif toks[i] +" "+toks[i+1][:3]+" "+toks[i+2]+" "+toks[i+3][:3]+" "+toks[i+4]=="IF NUM EQEQ NUM THEN":
			if toks[i+1][4:] == toks[i+3][4:]:
				i+=5
			else:
				i+= find_end(i,toks,"ENDIF")
		elif toks[i]+" "+toks[i+1][:3]+" "+toks[i+2]+" "+toks[i+3][:3]+" "+toks[i+4]=="IF VAR EQEQ NUM THEN":
			#print("value :",getValue(toks[i+1][4:])[8:])
			#print("num :",toks[i+3][4:])
			if getValue(toks[i+1][4:])[4:] == toks[i+3][4:]:
				i+=5
			elif getValue(toks[i+1][4:])[8:] == toks[i+3][4:]:
				i+=5
			else:
				i+= find_end(i,toks,"ENDIF")			

def run():
	data = open_file(argv[1])
	toks=lex(data)
	#print(toks)
	parser(toks)

run()
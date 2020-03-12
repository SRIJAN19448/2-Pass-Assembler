import re
opcode_dict=dict()
symbol_table=dict()     #format [name,type_variable/label,location_counter_address]    not finalised
literal_table=dict()

def opcode_initialise():                       #need to change ones to zero wherever necessary to account for no operand opcodes
    global opcode_dict
    opcode_dict['CLA']=['0000',0]
    opcode_dict['LAC']=['0001',1]
    opcode_dict['SAC']=['0010',1]
    opcode_dict['ADD']=['0011',1]
    opcode_dict['SUB']=['0100',1]
    opcode_dict['BRZ']=['0101',2]
    opcode_dict['BRN']=['0110',2]
    opcode_dict['BRP']=['0111',2]
    opcode_dict['INP']=['1000',1]
    opcode_dict['DSP']=['1001',1]
    opcode_dict['MUL']=['1010',1]
    opcode_dict['DIV']=['1011',1]
    opcode_dict['STP']=['1100',0]

class Pass_One:
    global opcode_dict
    global literal_table
    global symbol_table
    location_counter=0
    line_number=0           #later use for error handling
    error_found=False                                    #used to know if error is found so no second pass required
    fatal_error=False
    stop_found=False
    used_address=list()
    
    def __init__(self,file):
        self.filename=file
    
    def is_a_comment(self,str):
        return str.startswith("//")
    
    def has_a_label(self,str):
        a=str[0].find(':')
        if a!=-1:
            return True
        return False
    
    def extract_label(self,str):
        return str[0][:-1]

    def valid_opcode(self,str):
        a=opcode_dict.get(str,-2)
        if a==-2:
            return False
        return True

    def extract_opcode(self,str):
        return str[0]
 
    def extract_variable(self,str): 
        return str[1]

    def literal_already_exists(self,str):
        if literal_table.get(str,-2)==-2:
            return False
        return True
    
    def symbol_already_exists(self,str):
        if symbol_table.get(str,-2)==-2:
            return False
        return True

    def has_literal(self,str):
        a=str.find('=')
        if a==-1:
            return False
        return True

    def is_end_statement(self,str):
        if str.startswith("END"):
            return True
        return False

    def is_declarative_statement(self,str):
        if(len(str)!=3):
            return False
        if str[1]=='DW':
            return True
        return False

    def is_a_stop(self,str):                  #used to detect stop
        pass

    def is_start(self,str):                         #used to detect start of the assembly program
        pass

    def main(self):
        self.location_counter=0
        line_number=1
        file_assemble=open(self.filename,'r')
        file_temp=open("temp.txt",'w')
        file_error=open("error.txt",'w')
        file_symbol_table=open("symbol_table.txt",'w')
        file_literal_table=open("literal_table.txt",'w')

       
        for line in file_assemble:
            self.line_number+=1
            line=line.strip()
            operand=''
            opcode=''
            label=''
            length=0                               #maybe required not sure
            stop_found=False
            
            if self.is_end_statement(line):
                break
            
            if self.is_a_comment(line):             #checks for comment
                continue
            
            comm=line.find('//')                    #for comments after the assembly line
            if comm!=-1:
                line=line[:comm]
            line=line.strip()
            line=re.findall('\S+',line)

            if(len(line)==0):                     #for empty lines :/
                continue

            if(len(line)>3):                       #error for more operands
                file_error.write('More than required operands at line number ')
                file_error.write(str(self.location_counter))
                file_error.write('\n')
                self.error_found=True
                self.location_counter+=1
                continue


            if self.is_declarative_statement(line):       #make function for handling declarations here
                if self.location_counter>255:
                    file_error.write("Memory address out of bounds for instruction. \n")
                    self.fatal_error=True
                if not self.symbol_already_exists(line[0]):
                    symbol_table[line[0]]={'type':'variable','used':False,'defined':True,'address':self.location_counter,'value':line[2]}
                else:
                    if symbol_table[line[0]]['defined']==True:
                        file_error.write('Symbol '+line[0]+'declared multiple times \n')
                        self.fatal_error=True
                    elif symbol_table[line[0]]['type']=='label':
                        file_error.write('Label and variable with the same name '+label+'\n')
                        self.fatal_error=True
                    else:
                        symbol_table[line[0]]['defined']=True
                        symbol_table[line[0]]['address']=self.location_counter
                        symbol_table[line[0]]['value']=line[2]
                self.location_counter+=1
                continue                
            
            if self.has_a_label(line):
                label=self.extract_label(line)  #send it to symbol table later and check if it already exists for error reporting 
                line=line[1:]
                if not self.symbol_already_exists(label):
                    symbol_table[label]={'type':'label','used':False,'defined':True,'address':self.location_counter,'value':0}
                else:
                    if symbol_table[label]['type']=='variable':
                        file_error.write('Label and variable with the same name '+label+'\n')
                        symbol_table[label]['defined']=True
                        self.fatal_error=True
                        self.error_found=True
                    elif symbol_table[label]['defined']==True:
                        file_error.write('Label'+label+'declared multiple times')
                        self.fatal_error=True
                    else:
                        symbol_table[label]['address']=self.location_counter
                        symbol_table[label]['defined']=True
                self.location_counter+=1
  
            
            opcode=self.extract_opcode(line)
            if opcode=='START':
                continue
            if opcode=='STP':
                self.stop_found=True
            
            
            if self.valid_opcode(opcode):   #requires case for invalid for now
                a=opcode_dict.get(opcode)
                if a[1]!=0:                        #nothing done for literal yet
                    if(len(line)!=2):
                        file_error.write("operand not supplied for given operand at line number "+str(self.line_number)+'\n')
                        self.fatal_error=True
                        self.error_found=True
                        continue
                    operand=self.extract_variable(line)
                    if a[1]==2:
                        if not self.symbol_already_exists(operand):
                            symbol_table[operand]={'type':'label','used':True,'defined':False,'address':None,'value':0}
                        else:
                            symbol_table[operand]['used']=True
                        
                    elif self.has_literal(operand):
                        literal_table[operand]=(self.location_counter)

                        
                    else:
                        if not self.symbol_already_exists(operand):
                            symbol_table[operand]={'type':'variable','used':True,'defined':False,'address':None,'value':0}
                            if operand.isnumeric():
                                if int(operand)>255:
                                    file_error.write("Implicit address used is out of bounds for memory \n")
                                    self.fatal_error=True
                                symbol_table[operand]['defined']=True
                                symbol_table[operand]['address']=int(operand)
                                symbol_table[operand]['value']=operand
                                self.used_address.append(operand)
                        else:
                            symbol_table[operand]['used']=True

            else:                                       #write code for error reporting for invalid opcode
                file_error.write(line[0])
                file_error.write(' is an invalid opcode at line number ')
                file_error.write(str(self.location_counter))
                file_error.write('\n')
                self.error_found=True
                self.fatal_error=True
            
            file_temp.write(' '.join(line))                 #write to the temporary file
            file_temp.write('\n')
            
            self.location_counter+=1
        
        for i in symbol_table.keys():
            if symbol_table[i]['defined']==False:
                file_error.write('symbol ')
                file_error.write(i)
                file_error.write(' is used but not defined \n')

                if symbol_table[i]['type']=='variable':
                    while self.location_counter in self.used_address:
                        self.location_counter+=1
                    if self.location_counter>255:
                        file_error.write("Memory out of bounds. symbols can't be allocated memory anymore \n")
                        self.fatal_error=True
                        break
                    symbol_table[i]['address']=self.location_counter
                    symbol_table[i]['defined']=True
                    self.location_counter+=1
                else:
                    self.fatal_error=True
                    self.error_found=True
        if(self.stop_found==False):
            file_error.write('Stop not found in the program\n')
            file_temp.write('STP \n')

            
        file_temp.close()
        file_assemble.close()
        file_error.close()
        file_symbol_table.close()

class Pass_two:
    global symbol_table
    global opcode_dict
    global literal_table
    
    def __init__(self):
        self.filename='temp.txt'
    
    def main(self):
        file_open=open(self.filename,'r')
        file_output=open('output.txt','w')

        for line in file_open:
            line=line.rstrip()
            temp=False
            line=line.split(' ')
            opcode=line[0]
            type=opcode_dict[opcode][1]
            file_output.write(opcode_dict[opcode][0])
            if type!=0:
                var=line[1]
                try:
                    binary=bin(symbol_table[var]['address']).replace("0b",'')
                except:
                    binary=bin(literal_table[var]).replace("0b",'')
                l=8-len(binary)
                if l<0:
                    file_error=open('error.txt','a')
                    file_error.write('\n memory out of bounds')
                    file_error.write('\n fatal error: no output generated 5')
                    file_error.close()
                    temp=True
                    break

                    
                binary='0'*l+binary
                file_output.write(' ')
                file_output.write(binary)
            file_output.write('\n')
        file_output.close()
        if temp:
            file_output=open('output.txt','w')
            file_output.close()

def pass_one():
    filen=input("Enter the filename ")
    try:
        po=open(filen,'r')
        po.close()
    except:
        print("File do not exist. make sure its in the same directory and restart the programs")
        return
    obj=Pass_One(filen)
    obj.main()
    if obj.fatal_error==False:
        obj2=Pass_two()
        obj2.main()
    else:
        file_output=open('output.txt','w')
        file_output.close()
        file_error=open('error.txt','a')
        file_error.write('\n fatal error: no output generated \n ')
        file_error.close() 

opcode_initialise()
pass_one()

file_symbol_table=open('symbol_table.txt','w')                      #writing in the symbol table
for i in symbol_table.keys():
    file_symbol_table.write('Name:'+i)
    file_symbol_table.write('\t')
    file_symbol_table.write('Type: '+symbol_table[i]['type'])
    file_symbol_table.write('\t Value: '+str(symbol_table[i]['value']))
    file_symbol_table.write('\t Address'+str(symbol_table[i]['address']))
    file_symbol_table.write('\n')

file_symbol_table.close()

file_literal_table=open('literal_table.txt','w')                           #writing in the literal table
for i in literal_table.keys():
    file_literal_table.write('Name '+i+'\t')
    file_literal_table.write('Address ')
    file_literal_table.write(str(literal_table[i]))
    file_literal_table.write('\n')
file_literal_table.close()

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
    
    def __init__(self,file):
        self.filename=file
        pass
    
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
        pass

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
                file_error.write(self.location_counter)
                file_error.write('\n')
                self.error_found=True
                self.location_counter+=1
                continue


            if self.is_declarative_statement(line):       #make function for handling declarations here
                continue                
            
            if self.has_a_label(line):
                label=self.extract_label(line)  #send it to symbol table later and check if it already exists for error reporting 
                line=line[1:]
                if not self.symbol_already_exists(label):
                    symbol_table[label]={'type':'label','used':False,'defined':True,'address':self.location_counter,'value':0}
                else:
                    if symbol_table[label]['defined']==True:
                        file_error.write('Label'+label+'declared multiple times')
                    symbol_table[label]['address']=self.location_counter
                    symbol_table[label]['defined']=True

            file_temp.write(' '.join(line))                 #write to the temporary file
            file_temp.write('\n')  
            
            opcode=self.extract_opcode(line)
            if self.valid_opcode(opcode):   #requires case for invalid for now
                a=opcode_dict.get(opcode)
                if a[1]!=0:                        #nothing done for literal yet
                    operand=self.extract_variable(line)
                    if a[1]==2:
                        if not self.symbol_already_exists(operand):
                            symbol_table[operand]={'type':'label','used':True,'defined':False,'address':None,'value':0}
                        else:
                            symbol_table[operand]['used']=True
                        
                    elif self.has_literal(operand):
                        #operand=operand[2:-1] 
                        if not self.literal_already_exists(operand):
                            literal_table[operand]=(self.location_counter)
                        else:
                            pass                                                       #pass report error
                    else:
                        if not self.symbol_already_exists(operand):
                            symbol_table[operand]={'type':'variable','used':True,'defined':False,'address':None,'value':0}

            else:                                       #write code for error reporting for invalid opcode
                file_error.write(line[0])
                file_error.write(' is an invalid opcode at line number ')
                file_error.write(self.location_counter)
                file_error.write('\n')
                self.error_found=True
            
            self.location_counter+=1
        
        for i in symbol_table.keys():
            if symbol_table[i]['defined']==False:
                file_error.write('symbol ')
                file_error.write(i)
                file_error.write(' is used but not defined \n')

                if symbol_table[i]['type']=='variable':
                    symbol_table[i]['address']=self.location_counter
                    symbol_table[i]['defined']=True
                    self.location_counter+=1
                else:
                    self.fatal_error=True
                self.error_found=True
            
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
                binary='0'*l+binary
                file_output.write(' ')
                file_output.write(binary)
            file_output.write('\n')

def pass_one():
    filen=input("Enter the filename ")
    obj=Pass_One(filen)
    obj.main()
    if obj.fatal_error==False:
        obj2=Pass_two()
        obj2.main()
    else:
        file_error=open('error.txt','a')
        file_error.write('\n fatal error: no output generated 5')
        file_error.close()



opcode_initialise()
pass_one()
file_symbol_table=open('symbol_table.txt','w')
for i in symbol_table.keys():
    
    file_symbol_table.write('Name:'+i)
    file_symbol_table.write('\t')
    file_symbol_table.write('Type: '+symbol_table[i]['type'])
    file_symbol_table.write('\n')
file_symbol_table.close()



import re
opcode_dict=dict()
symbol_table=dict()     #format [name,type_variable/label,location_counter_address]    not finalised

def opcode_initialise():                       #need to change ones to zero wherever necessary to account for no operand opcodes
    global opcode_dict
    opcode_dict['CLA']=['0000',1]
    opcode_dict['LAC']=['0001',1]
    opcode_dict['SAC']=['0010',1]
    opcode_dict['ADD']=['0011',1]
    opcode_dict['SUB']=['0100',1]
    opcode_dict['BRZ']=['0101',1]
    opcode_dict['BRN']=['0110',1]
    opcode_dict['BRP']=['0111',1]
    opcode_dict['INP']=['1000',1]
    opcode_dict['DSP']=['1001',1]
    opcode_dict['MUL']=['1010',1]
    opcode_dict['DIV']=['1011',1]
    opcode_dict['STP']=['1100',1]

class Pass_One:
    global opcode_dict
    location_counter=0
    line_number=0           #later use for error handling
    error_found=False                                    #used to know if error is found so no second pass required
    
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
        return str[0]

    def valid_opcode(self,str):
        a=opcode_dict.get(str,-2)
        if a==-2:
            return False
        return True

    def extract_opcode(self,str):
        return str[0]
 
    def extract_variable(self,str): 
        return str[1]

    def is_assembler_directive(self,str):
        pass

    def has_literal(self,str):
        pass

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

    def check_type_of_instruction(self,str):           #check whether needs a variable or not
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
            if self.is_end_statement(line):
                break
                
            if self.is_a_comment(line):             #checks for comment
                continue
            comm=line.find('//')
            if comm!=-1:
                line=line[:comm]
            line=line.strip()
            line=re.findall('\S+',line)
            
            if(len(line)==0):                                    #for empty lines :/
                continue

            if(len(line)>3):                       #error for more operands
                pass
            
            file_temp.write(' '.join(line))                 #write to the temporary file
            file_temp.write('\n')

            if self.is_declarative_statement(line):       #make function for handling declarations here
                continue
                
            
            if self.has_a_label(line):
                label=self.extract_label(line)  #send it to symbol table later and check if it already exists for error reporting 
                line=line[1:]  
            
            opcode=self.extract_opcode(line)
            if self.valid_opcode(opcode):   #requires case for invalid for now
                a=opcode_dict.get(opcode)
                if a[1]==1:                        #nothing done for literal yet
                    operand=self.extract_variable(line)
            else:                                       #write code for error reporting for invalid opcode
                pass
            
            line_number+=1
            self.location_counter+=1
            
        file_temp.close()
        file_assemble.close()
        file_error.close()
        file_symbol_table.close()
   
def pass_one():
    filen=input("Enter the filename ")
    obj=Pass_One(filen)
    obj.main()

opcode_initialise()
pass_one()

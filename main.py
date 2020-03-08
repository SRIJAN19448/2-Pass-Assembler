import re
error=False
program_counter=0
op_table = dict()
symbol_table = []  # format [name,type_variable/label,location_counter_address]    not finalised
literal_table=[]
error_list=[]

def opcode_initialise():  # need to change ones to zero wherever necessary to account for no operand opcodes
    op_table['CLA'] = ['0000']
    op_table['LAC'] = ['0001']
    op_table['SAC'] = ['0010']
    op_table['ADD'] = ['0011']
    op_table['SUB'] = ['0100']
    op_table['BRZ'] = ['0101']
    op_table['BRN'] = ['0110']
    op_table['BRP'] = ['0111']
    op_table['INP'] = ['1000']
    op_table['DSP'] = ['1001']
    op_table['MUL'] = ['1010']
    op_table['DIV'] = ['1011']
    op_table['STP'] = ['1100']

def passOne(text):
    global program_counter
    global error
    global error_list
    STP=False                       #STP command found or not

    for a in text:
        if a=='' or a.startswith("//"):
            text.remove(a)

    for b in text:
        b=b.split(" ")
        for s in range(len(b)):
            if b[s].startswith("//"):
                b=b[:s]
                break

        if len(b)==1:
            if b[0]=="STP":
                STP=True
            elif b[0]!="CLA":
                error=True
                error_list.append("LESS ARGUMENTS THEN REQUIRED : " + str(b[0]))
        elif len(b)==2:
            if b[0][-1]==":":
                symb=b[0][:len(b[0])-1]
                flag=False
                for sym in symbol_table:
                    if sym['name']==symb:
                        if sym['found']==True:
                            error=True
                            error_list.append("MULTIPLE LABEL DECLARATION : " + sym['name'])
                        else:
                            sym['found']=True
                            sym['addr']=program_counter
                            flag=True
                if flag==False:
                    symbol_table.append({'name':symb ,'type':"label",'found':True,'used':False,'addr':program_counter})
                    
                if b[1] == "STP":
                    STP = True
                elif b[1] != "CLA":
                    error = True
                    error_list.append("INVALID OPCODE : " + b[1])
            elif b[0][0]=="B":
                if b[0]=="BRZ"or b[0]=="BRN" or b[0]=="BRP":
                    symb=b[1]
                    flag=False
                    for sym in symbol_table:
                        if sym['name']==symb:
                            sym['used']=True
                            flag=True
                    if flag==False:
                        symbol_table.append({'name':symb,'type':"label",'found':False,'used':True,'addr':-1})

                else:
                    error=True
                    error_list.append("INVALID OPCODE : " + b[0])
            else:
                if b[0] in op_table:
                    flag=False
                    if b[1][0]!="=":
                        for sym in symbol_table:
                            if sym['name'] == b[1]:
                                flag=True

                        if flag==False:
                            symbol_table.append({'name': b[1], 'type': "symbol",'addr': -1})
                    else:
                        flag=False
                        for lit in literal_table:
                            if lit['literal']==b[1]:
                                flag=True

                        if flag==False:
                            literal_table.append({'literal':b[1], 'addr':-1})

                else:
                    error=True
                    error_list.append("INVALID OPCODE")

        elif len(b)==3:
            if b[0] in op_table:
                error=True
                error_list.append("EXTRA ARGUMENTS THAN REQUIRED : " + b[0])
            elif b[0][-1]!=":":
                error=True
                error_list.append("INVALID COMMAND")
            else:
                symb = b[0][:len(b[0]) - 1]
                flag = False
                for sym in symbol_table:
                    if sym['name'] == symb:
                        if sym['found']==True:
                            error=True
                            error_list.append("MULTIPLE LABEL DECLARATION : " + sym['name'])
                        else:
                            sym['found'] = True
                            sym['addr'] = program_counter
                            flag = True
                if flag == False:
                    symbol_table.append({'name': symb, 'type': "label", 'found': True, 'used': False, 'addr': program_counter})

                if b[1] in op_table:
                    flag = False
                    if b[2][0]!="=":
                        for sym in symbol_table:
                            if sym['name'] == b[2]:
                                flag = True
                                continue
                        if flag == False:
                            symbol_table.append({'name': b[2], 'type': "symbol", 'found': False, 'used': True, 'addr': -1})
                    else:
                        flag = False
                        for lit in literal_table:
                            if lit['literal'] == b[2]:
                                flag = True

                        if flag == False:
                            literal_table.append({'literal': b[2], 'addr': -1})

                else:
                    error = True
                    error_list.append("INVALID OPCODE : " + b[1])
        program_counter+=1

    for y in symbol_table:
        if y['type']=="label":
            if y['found']==True and y['used']==False:
                error=True
                error_list.append("LABEL DEFINED BUT NOT USED")
            elif y['found']==False and y['used']==True:
                error=True
                error_list.append("LABEL NOT DEFINED")
    for y in symbol_table:
        try :
            c= int(y['name'])
            y['addr'] = c
            if c>=256:
                error=True
                error_list.append("ADDRESS OUT OF MEMORY: " + y['name'])
        except:
            pass
    for y in symbol_table:
        if y['type']=="symbol" and y['addr']==-1:
            y['addr']=program_counter
            program_counter+=1
    for y in literal_table:
        if y['addr']==-1:
            y['addr']=program_counter
            program_counter+=1


opcode_initialise()
     
while True:
    fileaddr = input("Input file address")
    try:
        file = open(fileaddr, 'r')
        break
    except :
        print("No File Found, Kindly Retry")


text = file.read()                              # read from the file
text = text.split('\n')
print(text)
passOne(text)
print(symbol_table)
print(literal_table)
print(error_list)

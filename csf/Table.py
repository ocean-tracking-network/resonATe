# -*- coding: utf-8 -*-
# Table -data structure inclues index(up to 9999), # of input (can be 0)
#       and message string
import csv
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(package_directory,'table.csv')

#Table data structure store index, number input values and message string
class Table(object):
    #build message table 
    def build(self):
        csvlist = csv.reader(open(csv_path,'rb'), delimiter=',')
        self=[['','']]*10000
        for index,number,message in csvlist:
            self[int(index)]=[number,message]
        return self
    #search for message
    def searchMessage(self,index):
        return self.build()[int(index)][1]
    def searchNumOfParm(self,index):
        return self.build()[int(index)][0]
    #update table content
    def insert(self,index_insert,numberofInput_insert,message_insert):
        table_list = []
        # Read all data from the csv file.
        with open(csv_path, 'rb') as file_open:
            table = csv.reader(file_open)
            table_list.extend(table)
        line_to_override={index_insert:[index_insert,numberofInput_insert,message_insert]}
        # Write data to the csv file and replace the lines in the line_to_override dict.
        with open(csv_path, 'wb') as file_write:
            writer = csv.writer(file_write)
            for line, row in enumerate(table_list):
                data = line_to_override.get(line,row)
                writer.writerow(data)
       
#message csf
def message(requestCode,index,numbOfParameters=0,inputString=None,param1=None,param2=None,param3=None,param4=None,param5=None,param6=None,param7=None,param8=None,param9=None,param10=None,callFrom=None):
        #initialize variables
        parm1=""
        parm2=""
        parm3=""
        parm4=""
        parm5=""
        parm6=""
        parm7=""
        parm8=""
        parm9=""
        parm10=""
        result=""
        parms_cnt=""
        parameters=""
        inputRequestCode=""
        simple=False
        concatenate=False
        table=Table()  #create table object  
        tablelist=table.build() #create list  
        
        #Save input parameters
        inputRequestCode=requestCode
        lookup_idx=index
        parms_cnt=numbOfParameters
        parm1=str(param1)
        parm2=str(param2)
        parm3=str(param3)
        parm4=str(param4)
        parm5=str(param5)
        parm6=str(param6)
        parm7=str(param7)
        parm8=str(param8)
        parm9=str(param9)
        parm10=str(param10) 
        
        #verify request code
        if(requestCode == 'simple'):
            simple=True
        elif(requestCode == 'concatenate'):
            concatenate=True    
        if(simple==False and concatenate==False):
            lookup_idx=12  #value for invalid message according to Table.csv 
            parms_cnt=1
            parm1=inputRequestCode
            result = table.searchMessage(lookup_idx).format(parm1)  
        
        if(simple or concatenate):
            #Check for valid index for message & Search null message 
            if(lookup_idx>(len(tablelist)-1) or lookup_idx<0):
                lookup_idx = 13  #value for invalid index according to Table.csv 
                parms_cnt=1
                parm1 = index
                result = table.searchMessage(lookup_idx).format(parm1)
            elif( table.searchMessage(lookup_idx)==''):
                lookup_idx = 11  # value for null message
                parms_cnt=1
                parm1 = index
                result = table.searchMessage(lookup_idx).format(parm1)
            
            else:#Insert parameters
                numOfParm = int(table.searchNumOfParm(lookup_idx))
                if(parms_cnt==numOfParm):
                    #insert param into message string
                    messageString = [parm1,parm2,parm3,parm4,parm5,parm6,parm7,parm8,parm9,parm10]
                    #check for null value,replace null by ?
                    parameters = (messageString[:numOfParm])
                    parameters= ['?' if x=='None' else x for x in parameters]
            
                    if(requestCode=='simple'):
                        result = table.searchMessage(lookup_idx).format(*parameters)
                    elif (requestCode=='concatenate'):
                        result = str(inputString)+'\n\n'+table.searchMessage(lookup_idx).format(*parameters)
                else:
                    # invalid input for number Of Parameters
                    lookup_idx = 14
                    result = table.searchMessage(lookup_idx).format(parms_cnt)
        return result
        
def main():
    #Create table & Test search function
    #table=Table()
    #print table.search(1)
    #Test insert function
    #table.insert(14,1,'Test')
    #Test simple request
    print message(requestCode='simple', index=10, numbOfParameters=1, inputString=None, param1='SystemIO', callFrom='Tester')
    #Test concatenate request
    #print message('concatenate',1,1,'Input','One')


if __name__ == '__main__':
    main()        
        
        
        
        
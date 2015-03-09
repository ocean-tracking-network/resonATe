# -*- coding: utf-8 -*-
"""
Created on Mon Mar 31 14:16:28 2014

@author: OTN -Jinyu
"""

import os
import sys
import csv
import shutil
import tempfile

# Get paths
SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

#Local Imports
import library.verifications as verify
import MessageDB as mdb
msgs = mdb.MessageDB()

def dis_mtx_merge(reqcode,distance_matrix_input,distance_real_input):
    #Variables
    file1_valid = False
    file2_valid = False
    encoding = None
    delimiter = ','
    file1=[]
    file1_base_name = distance_matrix_input[:-4]
    

    #Check reqcode 
    if(reqcode !='reqmerge'):
        #return 'Error:Not valid reqcode'  #CSF
        return msgs.get_message(12,[reqcode])
        
    if not verify.Filename( distance_matrix_input ):
        return msgs.get_message(15,[distance_matrix_input])
    if not verify.Filename( distance_real_input ):
        return msgs.get_message(15,[distance_real_input])
    
    #Assign file path
    #parent_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    parent_path = os.path.join(os.path.dirname(os.path.realpath(__file__)),os.pardir,os.pardir)
    distance_matrix_input = os.path.join(parent_path,'data', distance_matrix_input)
    distance_real_input = os.path.join(parent_path,'data', distance_real_input)
    
    #Check file exist
    if not verify.FileExists( distance_matrix_input ):
        return msgs.get_message(index=19,params=[distance_matrix_input])
    if not verify.FileExists( distance_real_input):
        return msgs.get_message(index=19,params=[distance_real_input])

    #backup detection file 1 (in a temp file)
    fd, file1_bckup_name = tempfile.mkstemp()
    shutil.copy2(distance_matrix_input,file1_bckup_name)
        
    #open first file
    file1_open = open(file1_bckup_name,'rb')
    
    #read first file
    file1_list = csv.reader(file1_open, delimiter=',')
    
    #file1 header  purpose for remove header in file1
    header1 = file1_list.next()
    
    #Store file1 content without header
    for row in file1_list:
        if(row):
            file1.append(row)
         
    #open second file
    file2_open=open(distance_real_input,'rb')
    
    #read second file
    file2_list = csv.reader(file2_open, delimiter=',')
    
    #file2 header
    header2 = file2_list.next()
    
    #real_distance column position in file2
    position = verify.headerPosition(header2,'real_distance')
    
    #test first file for validaity
    detection_headers_file1 = verify.FileHeaders(file1_bckup_name)
    #mandatory columns for 1st file
    mandatory_columns_file1 = ['stn1','stn2','distance_m','real_distance']
    missing_columns_file1 = verify.MandatoryColumns(detection_headers_file1,mandatory_columns_file1)
    if missing_columns_file1:
        return msgs.get_message(index=16,params=[missing_columns_file1,distance_matrix_input])
    else:
        file1_valid = True
    #test second file for validaity
    detection_headers_file2 = verify.FileHeaders(distance_real_input)
    #mandatory columns for 2nd file
    mandatory_columns_file2 = ['stn1','stn2','real_distance']    
    missing_columns_file2 = verify.MandatoryColumns(detection_headers_file2,mandatory_columns_file2)
    if missing_columns_file2:
        return msgs.get_message(index=16,params=[missing_columns_file2,distance_real_input])
    else:
        file2_valid = True
    #check for exist output file
    if(os.path.isfile(os.path.join(parent_path,'data', file1_base_name+'_merged.csv'))):
        return msgs.get_message(index=20,params=[file1_base_name+'_merged.csv'])
    #merge two files
    if(file1_valid and file2_valid):
        count_file1 = verify.FileCount(distance_matrix_input,header = True)
        count_file2 = verify.FileCount(distance_real_input,header = True)
        print msgs.get_message(index=17,params=[count_file1,distance_matrix_input])
        print msgs.get_message(index=17,params=[count_file2,distance_real_input])
        beforeUpdatedCount = verify.RealUpdateCount(file1_bckup_name)        
        
        #Check each row of file2         
        for row in file2_list:
            if(row):
                if ((position+1)>len(row) or len(header2) != len(row)):
                    return msgs.get_message(index=21,params=distance_real_input)
                if (row[position]!=''):
                    row_number = []
                    updateReal = ""
                    #Get station 1 and station 2 in file2
                    stn1 = row[verify.headerPosition(header2,'stn1')]
                    stn2 = row[verify.headerPosition(header2,'stn2')]
                    #Find station row number in file 1
                    row_number =  verify.stationMatch(file1_bckup_name,stn1,stn2)
                    #store real_distance value
                    updateReal = row[position]
                
                    #Update read_distance in file 1
                    for number in row_number:
                        update = []
                        update = file1[number]
                        update[verify.headerPosition(header1,'real_distance')]=updateReal #update real_distance
                        line_to_override = {int(number)+1:update}
                        #Get file1 content 
                        merged_file1 = []
                        a = open(file1_bckup_name, 'rb')
                        merged = csv.reader(a)
                        merged_file1.extend(merged)
                        a.close()
                        #Write to file1
                        b = open(file1_bckup_name, 'wb')
                        writer = csv.writer(b)
                        for line, row in enumerate(merged_file1):
                            data = line_to_override.get(line, row)
                            writer.writerow(data)
                        b.close()
        #output messages # of records & # of updated records 
        updatedCount = verify.RealUpdateCount(file1_bckup_name)
        
        file1_open.close()
        file2_open.close()                    
        #output the updated first file with 'merged' append to original file name
        if(updatedCount-beforeUpdatedCount > 0 ):
            print msgs.get_message(index=18,params=[updatedCount,file1_base_name+'_merged.csv'])
            shutil.copy(file1_bckup_name,''.join([parent_path,'/','data','/',file1_base_name,'_merged.csv']))
        else:
            print msgs.get_message(index=22,params=[distance_matrix_input])
            # remove bckup file
            if (os.path.isfile(file1_bckup_name)):
                os.remove(file1_bckup_name)
     
        return msgs.get_message(index=23)
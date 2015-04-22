# -*- coding: utf-8 -*-
"""
Distance matrix merge module v2

Author: Brian Jones
Version: 2.0
"""

import os
import sys
import pandas as pd

# Get paths
SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')
sys.path.append( CSF_PATH )

#Local Imports
import library.verifications as verify
import MessageDB as mdb
msgs = mdb.MessageDB()

def dis_mtx_merge(reqcode, distance_matrix_input, distance_real_input, 
                  data_directory='/home/sandbox/RStudio/data/'):
    
    # Variable Assignments
    reqcode = reqcode
    distance_matrix_input = distance_matrix_input
    distance_real_input = distance_real_input
    data_directory = data_directory
    
    # Check if reqcode is valid 
    if(reqcode !='reqmerge'):
        # return 'Error:Not valid reqcode'  #CSF
        return msgs.get_message(12,[reqcode])
    
    # Check for valid filenamesl
    if not verify.Filename( distance_matrix_input ):
        # return 'Error: {distance_matrix_input} variable supplied either 
        #             has invalid characters or does not contain a csv 
        #             file extension'
        return msgs.get_message(15,[distance_matrix_input])
    
    if not verify.Filename( distance_real_input ):
        # return 'Error: {distance_real_input} variable supplied either 
        #             has invalid characters or does not contain a csv 
        #             file extension'
        return msgs.get_message(15,[distance_real_input])
    
    # Create output file name & full path
    output_file = os.path.splitext(distance_matrix_input)[0]+'_merged.csv'
    output_file_path = os.path.join(data_directory, output_file)
    
    # Assign file paths
    distance_matrix_input_path = os.path.join(data_directory, 
                                              distance_matrix_input)
    distance_real_input_path = os.path.join(data_directory, 
                                            distance_real_input)

    # Check if both files exist
    if not verify.FileExists( distance_matrix_input_path ):
        # return: 'File {distance_matrix_input_path} does not exist'
        return msgs.get_message(index=19,params=[distance_matrix_input_path])
    
    if not verify.FileExists( distance_real_input_path):
        # return: 'File {distance_real_input_path} does not exist'
        return msgs.get_message(index=19,params=[distance_real_input_path])
    
    # Open the two files as pandas DataFrames
    matrix_df = pd.read_csv(distance_matrix_input_path, dtype='object')
    real_df = pd.read_csv(distance_real_input_path, dtype='object')
    
    # Mandatory columns for 1st matrix input file
    mandatory_columns_matrix = ['stn1','stn2','distance_m',
                                'real_distance','detec_radius1',
                                'detec_radius2']
    
    # Get column headers in each input file
    matrix_headers = list(matrix_df.columns)
    real_headers = list(real_df.columns)
    
    # Retrieve list of missing columns (based on column name matching)
    matrix_missing_columns = verify.MandatoryColumns(matrix_headers, 
                                                     mandatory_columns_matrix)
    
    # Return error message if missing any mandatory columns from the 
    # matrix input file
    if matrix_missing_columns:
        # return: 'Missing columns:{matrix_missing_columsn} in 
        #          file {distance_matrix_input}'
        return msgs.get_message(index=16,params=[matrix_missing_columns, 
                                                 distance_matrix_input_path])
        
    # Mandatory columns for the real distance input file
    mandatory_columns_real = ['stn1','stn2','real_distance',
                               'detec_radius1','detec_radius2'] 
       
    real_missing_columns = verify.MandatoryColumns(real_headers,
                                                   mandatory_columns_real)
    
    # Return error message if missing any mandatory columns from the 
    # real input file
    if real_missing_columns:
        return msgs.get_message(index=16,params=[real_missing_columns, 
                                                 distance_real_input_path])
    
    updates = 0 
    # Field update function (DRY)
    def field_update(df1, df2, field):
        '''
        return: number of updates
        '''
        updates = 0
        for index, row in df2[df2[field].notnull()].iterrows():
            df_index = df1.loc[((df1['stn1'] == row['stn1']) & 
                                (df1['stn2'] == row['stn2'])) | 
                               ((df1['stn2'] == row['stn1']) &
                                (df1['stn1'] == row['stn2']))]
            
            # continue only if station pare could be matched
            if not df_index.empty:
                if df1.loc[df_index.axes[0], field].item() != row[field]:
                    df1.loc[df_index.axes[0], field] = row[field]
                    updates += 1
            
        return updates
    
    # Update real_distance
    updates += field_update(matrix_df, real_df, 'real_distance')
    # Update detec_radius1
    updates += field_update(matrix_df, real_df, 'detec_radius1')
    # Update detec_radius2
    updates += field_update(matrix_df, real_df, 'detec_radius2')
    
    # Output merged file if update are performed
    if updates > 0:
        # print: There are {updates} records updated in file {output_file}
        print msgs.get_message(index=18, params=[updates, output_file])
        # Export the merged file
        matrix_df.to_csv(output_file_path, index= False)
    else:
        # print: There is no records update in {distance_matrix_input}
        print msgs.get_message(index=22, params=[distance_matrix_input])
        
    # return: Updates complete 
    return msgs.get_message(index=23)

if __name__ == '__main__':
    print dis_mtx_merge('reqmerge', 'matrix.csv','matrix_update.csv')
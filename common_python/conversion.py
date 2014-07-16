import os
import sys
import codecs
import chardet
import collections 

#Local Imports
import library.verifications as verify

# System paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
CSF_PATH = os.path.join(SCRIPT_PATH, os.pardir, 'csf')
sys.path.append(CSF_PATH)

from Table import message as msg

def conversion(input_file=None, input_encoding=None, data_dir='/home/sandbox/RStudio/data/'):
    '''
    Converts a file into utf-8 format
    '''
    # Variable input_file exists?
    if not input_file:
        print msg(requestCode='simple', index=200, numbOfParameters=1, param1='input_file')
        return ''
    
    input_file_path = os.path.join(data_dir,input_file)
    
    # Does the file at input_file_path exist?
    if not verify.FileExists(input_file_path):
        print msg(requestCode='simple', index=19, numbOfParameters=1, param1=input_file)
        return ''
    
    # Create output name
    version = verify.FileVersionID(input_file) # Get version ID
    if version:
        output_name = '{0}_utf8_v{1}.csv'.format(input_file[:-8],version)
    else:
        output_name = '{0}_utf8.csv'.format(input_file[:-4])
       
    output_file_path = os.path.join(data_dir, output_name)
    
    #Output file exists
    if verify.FileExists(output_file_path):
        print msg(requestCode='simple', index=20, numbOfParameters=1, param1=output_name)
        return ''  
    
    if not input_encoding: 
        encodings = []
        chunk_size = 100
        fh = open(input_file_path,'rU')
        while 1:
            chunk =fh.read(chunk_size)
            if not chunk: break
            encoding = chardet.detect(chunk)
            if encoding['encoding'] != 'ascii':
                encodings.append(encoding['encoding'])
        fh.close()
    
        counter=collections.Counter(encodings)

        if counter.most_common(1):
            detected_encoding = counter.most_common(1)[0][0]
        else:
            detected_encoding = 'ascii'
    
    if not input_encoding and not detected_encoding:
        print msg(requestCode='simple', index=201, numbOfParameters=0)
        return ''
    elif not input_encoding and detected_encoding:
        input_encoding = detected_encoding

    # Convert the file
    print msg(requestCode='simple', index=202, numbOfParameters=2,param1=input_file,param2=input_encoding),
    try:
        BLOCKSIZE = 1048576
        with codecs.open(input_file_path, "r", input_encoding) as sourceFile:
            with codecs.open(output_file_path, "w", "utf-8") as targetFile:
                while True:
                    contents = sourceFile.read(BLOCKSIZE)
                    if not contents:
                        break
                    targetFile.write(contents)
                    
        print msg(requestCode='simple', index=113,numbOfParameters=0)
        print msg(requestCode='simple', index=203, numbOfParameters=2,param1=input_file,param2=output_name)
        return ''
    except Exception as e:
        print e
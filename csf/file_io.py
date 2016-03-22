# -*- coding: utf-8 -*-
import codecs
import os
import sys
import csv

from cStringIO import StringIO
from chardet.universaldetector import UniversalDetector

SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
CSF_PATH = os.path.join(SCRIPT_PATH,os.pardir,'csf')

sys.path.append( CSF_PATH )
import MessageDB as mdb
msgs = mdb.MessageDB()

class fileIO():
    def __init__(self, reqcode=None, filename=None, fromto=None):
        # presistant variables
        self.fileh = None
        self.filename = ''
    
        if reqcode == 'reqopen':
            # Send open request
            self.fileIO(reqcode, filename, fromto)
        elif reqcode:
            # Tests to see if the file exists
            self.fileIO(reqcode, filename, fromto)
    
    def fileIO(self, reqcode=None, filename=None, fromto=None):
        '''
        
        Main function for processing reqcode requests
        
        '''
        reqcode = reqcode
        filename = filename
        fromto = fromto
        
        if reqcode == 'reqopen':
            self.open_file(filename)
        
        elif reqcode == 'reqseek0':
            ''' Set the self.fileh to seek to position 0 '''
            self.fileh.seek(0)
        
        elif reqcode == 'reqexist':
            # Return True if file exists
            return self.file_exists(filename) 
                    
        elif reqcode == 'reqread1':
            # Read one line of a file
            return self.read_one(filename, fromto)
        
        elif reqcode == 'reqread':
            # TODO: Not utilized
            pass
        elif reqcode == 'reqput':
            # TODO: Not utilized
            pass
        elif reqcode == 'reqclose':
            self.close_file()
        else:
            # Output message for an invalid request code
            return msgs.get_message(index=12, params=[reqcode])

    def open_file(self, filename):
        '''(str) -> NoneType
        
        Open a file handler using universal line mode
        
        '''
        self.fileh = open(filename, 'rU')
        self.filename = filename
    
    def close_file(self):
        '''fileIO -> NoneType
        Close the file handler 
        '''
        self.fileh.close()
        
    def file_exists(self, filename):
        ''' (fileIO, str) -> bool
        Tests for the existance of a file and returns True if the file exists, False
        if it doesn't.
        '''
        return os.path.isfile(filename)
    
    def read_one(self, filename, fromto):
        '''
        Read one line from the function and return as requested by fromto var
        '''
        # Set raw to be the first line of a input file
        raw = self.fileh.readline()
        
        # If line is blank, return None
        if not raw:
            return None
        
        # If BOM is detected, remove it from line
        raw = raw.decode('utf-8-sig', 'ignore')
        raw = raw.encode('utf-8')

        # Return row as a string 
        if fromto == ':string:':
            ''' Return string value of the first row in a file'''
            f = StringIO()
            f.write(raw)
            f.seek(0)
            return unicode(f.getvalue())
        
        # Return row as a list
        elif fromto == ':list:':
            ''' Return a list from comma separated values '''
            f = StringIO()
            f.write(raw)
            f.seek(0)
            reader = csv.reader(f)
            row = reader.next()
            return row
        else:
            return None  
        
    def __str__(self):
        return self.filename
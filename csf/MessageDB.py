# -*- coding: utf-8 -*-
# MessageDB -data structure inclues index, # of inputs (can be 0)
#       and message string
import csv
import os

package_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(package_directory,'table.csv')

def asint(s):
    try: return int(s[0]), ''
    except ValueError: return sys.maxint, s[0]

#MessageDB data structure store index, number input values and message string
class MessageDB(object):
    #build message table
    msgs = {}
    def __init__(self, input_file):
        csvlist = csv.reader(open(csv_path, 'rb'), delimiter=',')
        for x,paramcount,message in csvlist:
            if paramcount and message:
                self.msgs[x] = [int(paramcount),message]

    def getMessage(self, index, params=[], header=''):
        if header:
            header = '%s\n' % header
        # if it's a good message and it's in our table.
        if str(index) in self.msgs.keys(): # and len(params) == self.msgs[str(index)][0]:
            if len(params) == self.msgs[str(index)][0]:
                return header + self.msgs[str(index)][1].format(*params) # format and return it.
            else: # sanitize params to the expected length for the message as per M.M.
                if len(params) < self.msgs[str(index)][0]:  # if we're too short on parameters
                    params.extend(['?'] * (self.msgs[str(index)][0] - len(params))) # extend it with ?s.
                return self.getMessage(index,params[0:self.msgs[str(index)][0]]) # if we're too long this still works.
        elif str(index) not in self.msgs.keys(): # you asked for a message we don't have a code for.
            return header + self.getMessage(13, ['{}'.format(index)])
        # if you want to go back to a world where the user needs to get the number of parameters exactly right:
        # elif len(params) != self.msgs[str(index)][0]: # you don't have the right number of parameters for this message.
        #     return header + self.getMessage(14, ['%s' % index])
        else:       # return the 'you asked for the wrong message' message.
            return header + self.getMessage(0) # unknown error, no code for that yet. How did you manage to get here?

    def getNumParams(self,index):
        return self.msgs[str(index)][0]

    def getLength(self):
        return len(self.msgs)

    def getValidCodes(self):
        return self.msgs.keys()

    def isValidCode(self, idx):
        return str(idx) in self.msgs.keys()

    def putDefinition(self, idx, paramcount, message, force=False):
        if self.isValidCode(idx) and not force:
            print 'Code already exists for that index number ({}). Not inserting.'.format(idx)
            return -1
        else:
            self.msgs[idx]=[paramcount, message]


    def writeToCSV(self,out_csv):
        fp = open(out_csv, 'wb+')
        for i,x in sorted(self.msgs.iteritems(), key=asint): # sort by numeric key value for writing
            fp.write('{},{}\n'.format(i,','.join(map(str, x))))
        fp.close()


       
#message csf
def message(index,params=[],inputString=None):
        #initialize variables
        mdb=MessageDB(csv_path)  #create table object from csv

        if inputString is None:
            result = mdb.getMessage(index, params)
        else:
            result = '%s \n\n %s' % (inputString, mdb.getMessage(index, params))

        return result
        
def main():
    #Create table & Test search function
    mdb=MessageDB(csv_path)
    print mdb.isValidCode(1)
    #Test insert function
    print mdb.putDefinition(14,1,'Test {0}')
    print mdb.getMessage(14,['test'])
    #Test simple request with not enough parameters - as per M.M., should insert ? for missing params
    print mdb.getMessage(index=10, params=['SystemIO'])
    #Test with too many parameters. - as per M.M., should truncate extras and go through without complaint.
    print mdb.getMessage(index=3, params=['1', '2', '3', '4', '5', '6'])
    #Test concatenate request
    print mdb.getMessage(1,['One'],'Test Header:')
    mdb.writeToCSV('test_output.csv')
    # compare the test_output to the input csv
    import difflib
    d = difflib.Differ()
    s = list(d.compare(open('test_output.csv').readlines(), open('table.csv').readlines()))
    from pprint import pprint
    print 'File Differences:'
    pprint(s)
    print

if __name__ == '__main__':
    main()        
        
        
        
        
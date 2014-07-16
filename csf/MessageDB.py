# -*- coding: utf-8 -*-
# MessageDB -data structure inclues index, # of inputs (can be 0)
#       and message string
import csv
import os
import sys

package_directory = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(package_directory, 'message_table.csv')


def asint(s):
    try:
        return int(s[0]), ''
    except ValueError:
        return sys.maxint, s[0]


#MessageDB data structure store index, number input values and message string
class MessageDB(object):
    #build message table
    msgs = {}

    def __init__(self, input_file=None):
        if input_file is not None:
            csvlist = csv.reader(open(input_file, 'rb'), delimiter=',')
        else:
            csvlist = csv.reader(open(csv_path, 'rb'), delimiter=',')
        for x, paramcount, msg in csvlist:
            if paramcount and msg:
                self.msgs[x] = [int(paramcount), msg]

    def get_message(self, index, params=None, header=''):
        if params is None:
            params = []
        if header:  # if we're told we need to prepend some string...
            header = '%s\n' % header  # Attach a newline in preparation to combine it with the message output.
        # if it's a good message and it's in our table.
        if str(index) in self.msgs.keys():  # and len(params) == self.msgs[str(index)][0]:
            if len(params) == self.msgs[str(index)][0]:
                return header + self.msgs[str(index)][1].format(*params)  # format and return it.
            else:  # sanitize params to the expected length for the message as per M.M.
                if len(params) < self.msgs[str(index)][0]:  # if we're too short on parameters
                    params.extend(['?'] * (self.msgs[str(index)][0] - len(params)))  # extend it with ?s.
                return self.get_message(index, params[0:self.msgs[str(index)][0]])
        elif str(index) not in self.msgs.keys():  # you asked for a message we don't have a code for.
            return header + self.get_message(13, ['{}'.format(index)])
        # if you want to go back to a world where the user needs to get the number of parameters exactly right:
        # elif len(params) != self.msgs[str(index)][0]:  # wrong number of params for this message.
        #     return header + self.get_message(14, ['%s' % index])
        else:       # return the 'you asked for the wrong message' message.
            return header + self.get_message(114)   # unknown error, no code for that yet,
                                                    # using generic ERROR. How did you manage to get here?

    def get_num_params(self, index):
        return self.msgs[str(index)][0]

    def get_length(self):
        return len(self.msgs)

    def get_valid_codes(self):
        return self.msgs.keys()

    def is_valid_code(self, idx):
        return str(idx) in self.msgs.keys()

    def put_message(self, idx, paramcount, msg, force=False):
        if self.is_valid_code(idx) and not force:
            print 'Code already exists for that index number ({}). Not inserting.'.format(idx)
            return -1
        else:
            self.msgs[idx] = [paramcount, msg]

    def write_to_csv(self, out_csv):
        fp = open(out_csv, 'wb+')
        for i, x in sorted(self.msgs.iteritems(), key=asint):  # sort by numeric key value for writing
            fp.write('{},{}\n'.format(i, ','.join(map(str, x))))
        fp.close()


#message csf
def message(index, params=None, input_string=None):
        if params is None:
            params = []
        # initialize variables
        mdb = MessageDB(csv_path)  # create table object from csv

        if input_string is None:
            result = mdb.get_message(index, params)
        else:
            result = '%s \n\n %s' % (input_string, mdb.get_message(index, params))

        return result


def main():
    #Create table & Test search function
    mdb = MessageDB(csv_path)
    print mdb.is_valid_code(1)
    #Test insert function
    print mdb.put_message(14, 1, 'Test {0}')
    print mdb.get_message(14, ['test'])
    #Test simple request with not enough parameters - as per M.M., should insert ? for missing params
    print mdb.get_message(index=10, params=['SystemIO'])
    #Test with too many parameters. - as per M.M., should truncate extras and go through without complaint.
    print mdb.get_message(index=3, params=['1', '2', '3', '4', '5', '6'])
    #Test concatenate request
    print mdb.get_message(1, ['One'], 'Test Header:')
    mdb.write_to_csv('test_output.csv')
    # compare the test_output to the input csv
    import difflib
    d = difflib.Differ()
    s = list(d.compare(open('test_output.csv').readlines(), open('message_table.csv').readlines()))
    from pprint import pprint
    print 'File Differences:'
    pprint(s)
    print

if __name__ == '__main__':
    main()
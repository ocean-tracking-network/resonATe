# -*- coding: utf-8 -*-

import unittest
import sys
import os
import pandas as pd
import codecs
import StringIO

from detectionmaker import detection_maker as dm

# System paths
SCRIPT_PATH = os.path.dirname(os.path.abspath(__file__))
COMMON_PATH = os.path.join(SCRIPT_PATH, os.pardir)
DATA_PATH = os.path.abspath(os.path.join(SCRIPT_PATH,
                                         os.pardir,
                                         os.pardir,
                                         'data'))

sys.path.append(COMMON_PATH)
from common_python import load_detections
from common_python import filter_detections
from common_python import dis_mtrx_merge
from common_python import conversion
from common_python import cleanup
from common_python import interval_data_tool


# Class to capture standard output used for assertions
class capture_stdout():
    def __init__(self):
        self.stdout = sys.stdout
        self.outstring = StringIO.StringIO()
        sys.stdout = self.outstring
    
    def release_output(self):
        sys.stdout = self.stdout
        self.outstring.seek(0)
        return self.outstring.read()


class TestSandbox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSandbox, cls).setUpClass()
        dm.detectionMaker(seed=100,animals=(10,100),
                          animal_speed=(10,22),
                          csvfile='../../data/sandbox_test.csv')
    
    def setUp(self):
        unittest.TestCase.setUp(self)
        
    def test_01_load_detections(self):
        stdout = capture_stdout() # Capture output
        
        # Load the generated detection file
        load_detections.loadDetections(detection_file='sandbox_test.csv',
                                       version_id='00', 
                                       DistanceMatrix=True, 
                                       ReloadInputFile=True, 
                                       SuspectDetections=True, 
                                       time_interval='60',
                                       data_directory=DATA_PATH)
        
        output =  stdout.release_output() # Release output
        print output
        
        #Assertions
        self.assertIn('File loaded successfully! Detection Count: 66', output, 'Correct Detections')
        self.assertIn('There are 3 suspect detections', output, '3 Suspects?')
        self.assertIn('There are 13 station matrix pairs', output, '13 station matrix pairs?')
    
    def test_02_filter_detections(self):
        stdout = capture_stdout() # Capture output
        
        # Filter detections (depends on test 1 passing)
        print filter_detections.filterDetections(detection_file='sandbox_test.csv',
                                           version_id='00',
                                           SuspectFile='sandbox_test_suspect_v00.csv',
                                           OverrideSuspectDetectionFile=False, 
                                           DistanceMatrix=True, 
                                           ReloadInputFile=False,
                                           data_directory=DATA_PATH)
        
        output =  stdout.release_output() # Release output
        print output
        
        #Assertions
        self.assertIn('1 suspect detections removed', output, 'Remove 1 suspect detections')
        self.assertIn('Total detections in output file: 65', output, '65 detections left')
        self.assertIn('There are 13 station matrix pairs', output, '13 station matrix pairs?')
        
    def test_03_dis_mtrx_merge(self):
        stdout = capture_stdout()
                
        csv_file = pd.read_csv('../../data/sandbox_test_distance_matrix_v00.csv')
        #Add a real_distance
        csv_file.loc[3,'real_distance'] = 310000
        
        # Save the modified file
        csv_file.to_csv('../../data/sandbox_test_distance_matrix_fix.csv',
                        index=False)
        
        print dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                    distance_matrix_input='sandbox_test_distance_matrix_v00.csv',
                                    distance_real_input='sandbox_test_distance_matrix_fix.csv')
        
        output = stdout.release_output()
        print output
        
        #Assertions
        self.assertIn('There are 1 records updated in file sandbox_test_dis' \
                      'tance_matrix_v00_merged.csv', 
                      output, '1 record updated?')
        
    def test_04_conversion(self):
        stdout = capture_stdout()
                
        # Open sample file and convert to japanese shift-jis encoding
        BLOCKSIZE = 1048576 # or some other, desired size in bytes
        with codecs.open('../../data/sandbox_test.csv', "r", "utf-8") as sourceFile:
            with codecs.open('../../data/sandbox_test_japanese.csv', "w", "shift-jis") as targetFile:
                while True:
                    contents = sourceFile.read(BLOCKSIZE)
                    if not contents:
                        break
                    targetFile.write(contents)
                    
        # Read the file into a dataframe
        df = pd.read_csv('../../data/sandbox_test.csv', encoding='shift-jis')
        
        # Replace the station names to start with Yen symbol
        df.station = df.station.replace('^P',u'￥',regex=True)
        
        # Save the modified file
        df.to_csv('../../data/sandbox_test_japanese.csv',
                        index=False, encoding='shift-jis')
        
        print conversion.conversion(input_file='sandbox_test_japanese.csv',
                                    input_encoding='shift-jis',
                                    data_dir=DATA_PATH)
        
        output = stdout.release_output()
        print output
        
        #Assertions
        self.assertIn('Converting file \'sandbox_test_japanese.csv\'', output, 'Converting file')
        self.assertIn('utf-8 as \'sandbox_test_japanese_utf8.csv\'.', output, 'Conversion finished')
    
    def test_05_interval_data(self):
        stdout = capture_stdout()
        interval_data_tool.intervalData('sandbox_test.csv',
                                        'sandbox_test_distance_matrix_v00.csv',
                                        data_directory=DATA_PATH)
        
        output = stdout.release_output()
        print output
    
    # def test_06_cleanup(self):
    #     stdout = capture_stdout()
    #
    #     #Run cleanup driver
    #     cleanup.cleanup(reqcode='reqcleanup')
    #
    #     output = stdout.release_output()
    #     print output
    #
    #     #Assertions
    #     self.assertIn('tables have been dropped', output, 'Tables dropped?')
    #     self.assertIn('public.\"sandbox_test_v00\"', output, 'First table')
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)

    @classmethod
    def tearDownClass(cls):
        super(TestSandbox, cls).tearDownClass()
        files = [x for x in os.listdir(DATA_PATH) if 'sandbox_test' in x]
        for file in files:
            os.remove(os.path.join(DATA_PATH,file))

if __name__ == '__main__':
    test = unittest.main()
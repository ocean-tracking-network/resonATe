# -*- coding: utf-8 -*-
import unittest
import sys
import os
import StringIO
import shutil
from os import path

# SETUP DIRECTORY PATHS 
SCRIPT_PATH = path.dirname( path.abspath(__file__) )
COMMONPY_PATH = os.path.join(SCRIPT_PATH, os.pardir)
DATA_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, 'data'))

TESTFILE_PATH = path.join(SCRIPT_PATH, 'test_files', 'use_tests')

# Import the common python functions
sys.path.append(COMMONPY_PATH)
from common_python import load_detections
from common_python import filter_detections
from common_python import dis_mtrx_merge
from common_python import conversion
from common_python import compress
from common_python import cohorts
from common_python import uniqueid
from common_python import cleanup
from common_python import interval_data_tool


# Class to capture standard output used for assertion testing
class capture_stdout():
    def __init__(self):
        self.stdout = sys.stdout
        self.outstring = StringIO.StringIO()
        sys.stdout = self.outstring
    
    def release_output(self):
        sys.stdout = self.stdout
        self.outstring.seek(0)
        return self.outstring.read()

# Used to retrieve all files currently 
def getfiles():
    for fileh in os.listdir(DATA_PATH):
        shutil.copy(path.join(DATA_PATH, fileh), 
                    '/home/sandbox/RStudio/sandbox/test/cache/')
        
class TestSandbox(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestSandbox, cls).setUpClass()
        # Show diff when multi-line assertion fails
        cls.maxDiff = None 
        
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        
        # Mute the cleanup process output
        stdout = capture_stdout()
        
        # Run database cleanup after each function test
        cleanup.cleanup(reqcode='reqcleanup')
           
        # Remove all the testing files
        for testfile in os.listdir(DATA_PATH):
            os.remove(os.path.join(DATA_PATH, testfile))
        
        # Release output    
        stdout.release_output()
        
    def test_01_load_detections(self):
        #
        #    TEST 1 - Tests the load_detection module using the default input
        #
        fldr = 'test1' # Test folder name
        
        #File Names
        input_detect_file = 'test1_detections.csv'
        output_matrix_file = 'test1_detections_distance_matrix_v00.csv'
        output_suspect_file = 'test1_detections_suspect_v00.csv'
        expected_output_file = 'test1_expected_output.txt'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the test file into the data folder to be executed by the load_detections script
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)
        
        # Run the load_detections function on the test file
        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00', 
                                       DistanceMatrix=True, 
                                       ReloadInputFile=True, 
                                       SuspectDetections=True, 
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)
        
        # Release console output
        output =  stdout.release_output() # Release output
        
        
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Test Comparison of output to expected output
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        # File output
        # Matrix File
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_matrix_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_matrix_file)).read())
        
        # Suspect File
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_suspect_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_suspect_file)).read())
    
    def test_02_filter_detections(self):
        #
        #    TEST 2 - filter_detections module testing with good input files 
        #
        fldr = 'test2' # Test folder name
        
        #File Names
        input_detect_file = 'test2_detections.csv'
        input_suspect_file = 'test2_suspects.csv'
        output_matrix_file = 'test2_detections_distance_matrix_v01.csv'
        output_detection_file = 'test2_detections_v01.csv'
        expected_output_file = 'test2_expected_output.txt'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)
        
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_suspect_file), DATA_PATH)
                
        
        # Run the load_detections function on the test file
        filter_detections.filterDetections(detection_file=input_detect_file,
                                           version_id='00',
                                           SuspectFile=input_suspect_file,
                                           OverrideSuspectDetectionFile=True, 
                                           DistanceMatrix=True, 
                                           ReloadInputFile=True,
                                           detection_radius='',
                                           data_directory=DATA_PATH)
        
        # Release console output
        output =  stdout.release_output() # Release output
        
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Test Comparison of output to expected output
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        # File output
        # Matrix File
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_matrix_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_matrix_file)).read())
        
        # Suspect File
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_detection_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_detection_file)).read())
        
    def test_03_dis_mtrx_merge(self):
        #
        #    TEST 3 - distance matrix merge testing with standard input files
        #
        fldr = 'test3' # Test folder name
        
        #File Names
        matrix_1_file = 'test3_distance_matrix_input1.csv'
        matrix_2_file = 'test3_distance_matrix_input2.csv'
        
        output_matrix_file = 'test3_distance_matrix_input1_merged.csv'
        
        expected_output_file = 'test3_expected_output.txt'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)
        
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)
                
        
        # Run the load_detections function on the test file
        print dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                    distance_matrix_input= matrix_1_file,
                                    distance_real_input= matrix_2_file,
                                    data_directory=DATA_PATH)

        # Release console output
        output =  stdout.release_output() # Release output
        
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        # Merged Matrix File comparison
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_matrix_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_matrix_file)).read())

    def test_04_uniqueid(self):
        #
        #    TEST 4 - Run the uniqueid module using a file which doesn't have a 
        #            unqdetecid column.
        #
        fldr = 'test4' # Test folder name
        
        # File Names
        detection_file = 'test4_detections.csv'
        output_unique_file = 'test4_detections_unqid.csv'
        expected_output_file = 'test4_expected_output.txt'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the detection file into the test data directory
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)
                
        # Run the load_detections function on the test file
        uniqueid.add_column_unqdetecid(detection_file, DATA_PATH)

        # Release console output
        output =  stdout.release_output() # Release output
        
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        
        # Compare files with unqdetecid columns
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_unique_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_unique_file)).read()) 

    def test_04a_uniqueid(self):
        #
        #    TEST 4a - run uniqueid function when output file already exists
        #
        fldr = 'test4a' # Test folder name
        
        #File Names
        detection_file = 'test4a_detections.csv'
        output_unique_file = 'test4a_detections_unqid.csv'
        expected_output_file = 'test4a_expected_output.txt'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)
        
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              output_unique_file), DATA_PATH)
                
        # Run the uniqueid function which will fail due to the output already existing
        uniqueid.add_column_unqdetecid(detection_file, DATA_PATH)

        # Release console output
        output =  stdout.release_output() # Release output
        
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_04b_uniqueid(self):
        #
        #    TEST 4b - run uniqueid function when the unqdetecid column already exists
        #
        fldr = 'test4b' # Test folder name
        
        #File Names
        detection_file = 'test4b_detections_unqid.csv'
        expected_output_file = 'test4b_expected_output.txt'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the detection file into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)
                
        # Run the uniqueid function. add_column_unqdetecid is expected to fail
        # because unqdetecid column already exists
        uniqueid.add_column_unqdetecid(detection_file, DATA_PATH)

        # Release console output
        output =  stdout.release_output() # Release output
        
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)
                   
    def test_05_compress(self):
        #
        #    Test 5 - Run a test on the compress module using a good detection  
        #                file input.
        #
        fldr = 'test5' # Test folder name
        
        #File Names
        detection_file = 'test5_detections.csv'
        output_compressed_file = 'test5_detections_compressed_detections_v00.csv'
        expected_output_file = 'test5_expected_output.txt'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the detection file into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)
                
        # Execute the compression function
        compress.CompressDetections(detection_file, DATA_PATH)
            
        # Release console output
        output =  stdout.release_output() # Release output
        
        # Read expected output into a string
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        
        # Compare files with unqdetecid columns
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_compressed_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_compressed_file)).read())    
            
    def test_06_cohorts(self):
        #
        #    TEST 6 - runs the cohort module using good inputs
        #
        fldr = 'test6' # Test folder name
        
        # File Names
        compressed_file = 'test6_compressed_detections.csv'
        expected_output_file = 'test6_expected_output.txt'
        output_cohort_file = 'test6_compressed_detections_cohort_60min.csv'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the testing files needed for the cohort step into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              compressed_file), DATA_PATH)
                
        # Execute the cohort function with 60 minute interval time
        cohorts.CohortRecords(interval_time=60, 
                              compressed_file=compressed_file, 
                              data_directory=DATA_PATH)
            
        # Release console output
        output =  stdout.release_output() # Release output
        
        # Read expected output into a string
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        
        # Compare files with the cohort 
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_cohort_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_cohort_file)).read())

    def test_07_conversion(self):
        #
        #    TEST 7 - Test using an ANSI windows-1252 format. Loading steps fails 
        #                unless file is converted using the conversion module.
        #
        fldr = 'test7' # Test folder name
        
        #File Names
        input_detect_file = 'test7_detections.csv'
        expected_output_file = 'test7_expected_output.txt'
        output_converted_file = 'test7_detections_utf8.csv'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the testing files
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)
                
        # Execute the load_detection function to get expected failure
        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00', 
                                       DistanceMatrix=True, 
                                       ReloadInputFile=True, 
                                       SuspectDetections=True, 
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)

        # Run the utf-8 conversion function on the windows-1252 formatted file
        conversion.conversion(input_detect_file, data_dir=DATA_PATH)
        
        # Execute the same loading function with the converted file which is now 
        # expected to pass
        load_detections.loadDetections(detection_file=output_converted_file,
                                       version_id='00', 
                                       DistanceMatrix=True, 
                                       ReloadInputFile=True, 
                                       SuspectDetections=True, 
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)
                
        # Release console output
        output =  stdout.release_output() # Release output
        
        # Read expected output into a string
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        # Compare the utf-8 converted files 
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_converted_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_converted_file)).read())
        
    def test_08_interval_datatool(self):
        #
        #    TEST 8 - Test of the interval data tool using good input files.
        #
        fldr = 'test8' # Test folder name
        
        #File Names
        input_detect_file = 'test8_detections.csv'
        input_dist_mtrx_file = 'test8_distance_matrix.csv'
        expected_output_file = 'test8_expected_output.txt'
        output_interval_file = 'test8_detections_interval_data_v00.csv'
        output_compressed_file = 'test8_detections_compressed_detections_v00.csv'
        
        # Capture console output to compare to what is expected
        stdout = capture_stdout()
        
        # Copy the testing files needed for the interval data module, a distance matrix 
        # and a detection file
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_dist_mtrx_file), DATA_PATH)
                
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        # Run the interval_dat_tool
        interval_data_tool.intervalData(input_detect_file, 
                                        input_dist_mtrx_file, 
                                        DATA_PATH)

        # Release console output
        output =  stdout.release_output() # Release output
        
        # Read expected output into a string
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()
                                       
        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)
        
        
        # Compare the interval data outputs
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                                 output_interval_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                                 output_interval_file)).read())
        
        self.assertMultiLineEqual(open(path.join(DATA_PATH,
                                         output_compressed_file)).read(), 
                                  open(path.join(TESTFILE_PATH, fldr,
                                         output_compressed_file)).read())
if __name__ == '__main__':
    unittest.main()
    
    
    
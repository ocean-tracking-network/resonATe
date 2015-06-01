# -*- coding: utf-8 -*-
import unittest
import sys
import os
import StringIO
import shutil
from os import path

# SETUP DIRECTORY PATHS 
SCRIPT_PATH = path.dirname(path.abspath(__file__))
COMMONPY_PATH = os.path.join(SCRIPT_PATH, os.pardir)
DATA_PATH = os.path.abspath(os.path.join(SCRIPT_PATH, 'data'))

TESTFILE_PATH = path.join(SCRIPT_PATH, 'test_files', 'use_tests')

# Import the common python functions
sys.path.append(COMMONPY_PATH)


# Class to capture standard output used for assertion testing
class CaptureStdout:
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
        from common_python import cleanup

        unittest.TestCase.tearDown(self)

        # Mute the cleanup process output
        stdout = CaptureStdout()

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
        from common_python import load_detections

        fldr = 'test1'  # Test folder name

        # File Names
        input_detect_file = 'test1_detections.csv'
        output_matrix_file = 'test1_detections_distance_matrix_v00.csv'
        output_suspect_file = 'test1_detections_suspect_v00.csv'
        expected_output_file = 'test1_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

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
        output = stdout.release_output()  # Release output
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

    def test_01a_load_detections(self):
        #
        #    TEST 1a - More headers than data columns
        #
        from common_python import load_detections

        fldr = 'test1a'

        # File names
        input_detect_file = 'sample_extra_header.csv'
        expected_output_file = 'test1a_expected_output.txt'

        # Capture output
        stdout = CaptureStdout()

        # Copy files into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)
        # Release output
        output = stdout.release_output()

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_01b_load_detections(self):
        #
        #    TEST 1b - Test file missing column name in header record
        #
        from common_python import load_detections

        fldr = 'test1b'

        # File names
        input_detect_file = 'sample_missing_header.csv'
        expected_output_file = 'test1b_expected_output.txt'

        # Capture output
        stdout = CaptureStdout()

        # Copy files into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)
        # Release output
        output = stdout.release_output()

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_01c_load_detections(self):
        #
        #    TEST 1c - Test file missing column name
        #
        from common_python import load_detections

        fldr = 'test1c'

        # File names
        input_detect_file = 'sample_missing_cols.csv'
        expected_output_file = 'test1c_expected_output.txt'

        # Capture output
        stdout = CaptureStdout()

        # Copy files into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)
        # Release output
        output = stdout.release_output()

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_01d_load_detections(self):
        #
        #    TEST 1d - unqdetecid column is not unique
        #
        from common_python import load_detections

        fldr = 'test1d'

        # File names
        input_detect_file = 'sample_not_unique.csv'
        expected_output_file = 'test1d_expected_output.txt'

        # Capture output
        stdout = CaptureStdout()

        # Copy files into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)
        # Release output
        output = stdout.release_output()

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_01e_load_detections(self):
        #
        #    TEST 1e - detection_radius variable is invalid - acceptable range is 0 - 999
        #
        from common_python import load_detections

        fldr = 'test1e'

        # File names
        input_detect_file = 'test1e_detections.csv'
        expected_output_file = 'test1e_expected_output.txt'

        # Capture output
        stdout = CaptureStdout()

        # Copy files into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        low_detection_radius = -1
        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius=low_detection_radius,
                                       data_directory=DATA_PATH)

        high_detection_radius = 1000
        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius=high_detection_radius,
                                       data_directory=DATA_PATH)

        # Release output
        output = stdout.release_output()

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_01f_load_detections(self):
        #
        #    TEST 1f - detection_radius variable is valid - acceptable range is 0 - 999
        #
        from common_python import load_detections

        fldr = 'test1f'

        # File names
        input_detect_file = 'test1f_detections.csv'
        expected_output_file = 'test1f_expected_output.txt'
        output_detect_file = 'test1f_detections_v01.csv'

        # Capture output
        stdout = CaptureStdout()

        # Copy files into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        detection_radius = 400
        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius=detection_radius,
                                       data_directory=DATA_PATH)

        # Release output
        output = stdout.release_output()

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_02_filter_detections(self):
        #
        #    TEST 2 - filter_detections module testing with good input files 
        #
        from common_python import filter_detections

        fldr = 'test2'  # Test folder name

        # File Names
        input_detect_file = 'test2_detections.csv'
        input_suspect_file = 'test2_suspects.csv'
        output_matrix_file = 'test2_detections_distance_matrix_v01.csv'
        output_detection_file = 'test2_detections_v01.csv'
        expected_output_file = 'test2_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

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
        output = stdout.release_output()  # Release output

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

    def test_02a_filter_detections(self):
        #
        #    TEST 2 - filter_detections module testing with special cases

        ## SPECIAL CASES
        # test cases in file
        # single detection: catnum SMPL-single not a release (flagged)
        # single detection: catnum SMPL-424  release ( not flagged)
        # only two detections with long time between: catnum SMPL-only_two neither a release (2nd one flagged)
        # long time between first two detections 1st one a release: catnumb SMPL-418 (9 hours) Not flagged
        # long time between last two detections: catnumb   SMPL-418 (1 day) flagged
        # long time between first two detections no release: catnumb   SMPL-419 (1 day) flagged
        # three detections with release long time between all:  catnum SMPL-420 (both flagged)
        # three detections with no release long time between first two::  catnum SMPL-421

        from common_python import load_detections
        from common_python import filter_detections

        fldr = 'test2a'  # Test folder name

        # File Names
        input_detect_file = 'sample_matched_detections_2013_special_cases.csv'
        input_suspect_file = 'sample_matched_detections_2013_override_suspect.csv'
        expected_output_file = 'test2a_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_suspect_file), DATA_PATH)

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
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Test Comparison of output to expected output
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03_dis_mtrx_merge(self):
        #
        #    TEST 3 - distance matrix merge testing with standard input files
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3'  # Test folder name

        # File Names
        matrix_1_file = 'test3_distance_matrix_input1.csv'
        matrix_2_file = 'test3_distance_matrix_input2.csv'

        output_matrix_file = 'test3_distance_matrix_input1_merged.csv'

        expected_output_file = 'test3_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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

    def test_03a_dis_mtrx_merge(self):
        #
        #   Test 03a -
        #           original file has extra header
        #           override file missing columns
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3a'  # Test folder name

        # File Names
        matrix_1_file = 'sample_matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'sample_extra_header_dm.csv'

        expected_output_file = 'test3a_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03b_dis_mtrx_merge(self):
        #
        #   Test 03b - override file missing column name
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3b'  # Test folder name

        # File Names
        matrix_1_file = 'matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'sample_missing_cols_dm_all.csv'

        expected_output_file = 'test3b_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03c_dis_mtrx_merge(self):
        #
        #   Test 03c - Missing columns
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3c'  # Test folder name

        # File Names
        matrix_1_file = 'sample_missing_cols_dm_all.csv'
        matrix_2_file = 'matched_detections_2013_distance_matrix.csv'

        expected_output_file = 'test3c_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03d_dis_mtrx_merge(self):
        #
        #   Test 03d - Both files missing all columns
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3d'  # Test folder name

        # File Names
        matrix_1_file = 'sample_missing_cols_dm_all.csv'
        matrix_2_file = 'sample_missing_cols_dm_all.csv'

        expected_output_file = 'test3d_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03e_dis_mtrx_merge(self):
        #
        #   Test 03e - first file is full
        #              second file is missing column names
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3e'  # Test folder name

        # File Names
        matrix_1_file = 'sample_missing_cols_dm_all.csv'
        matrix_2_file = 'sample_missing_cols_dm_header.csv'

        expected_output_file = 'test3e_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03f_dis_mtrx_merge(self):
        #
        #   Test 03f - first file is full
        #              second file is missing column names
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3f'  # Test folder name

        # File Names
        matrix_1_file = 'sample_missing_header_dm.csv'
        matrix_2_file = 'sample_matched_detections_2013_distance_matrix.csv'

        expected_output_file = 'test3f_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03g_dis_mtrx_merge(self):
        #
        #   Test 03g - first file is full
        #              second file is missing column names
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3g'  # Test folder name

        # File Names
        matrix_1_file = 'sample_matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'sample_extra_header_dm.csv'

        expected_output_file = 'test3g_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03h_dis_mtrx_merge(self):
        #
        #   Test 03h - missing the first input file
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3h'  # Test folder name

        # File Names
        matrix_1_file = 'missing_matched_detections_2013_distance_matrix_v01.csv'
        matrix_2_file = 'sample_extra_header_dm.csv'

        expected_output_file = 'test3h_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03i_dis_mtrx_merge(self):
        #
        #   Test 03i - missing the override file
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3i'  # Test folder name

        # File Names
        matrix_1_file = 'sample_matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'missing_overrid.csv'

        expected_output_file = 'test3i_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03j_dis_mtrx_merge(self):
        #
        #   Test 03j - real_distance in override is a non numeral value
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3j'  # Test folder name

        # File Names
        matrix_1_file = 'matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'override_dist_mtrx_notnum_real.csv'

        expected_output_file = 'test3j_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03k_dis_mtrx_merge(self):
        #
        #   Test 03k - detect1 column in override file has a non numeral value
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3k'  # Test folder name

        # File Names
        matrix_1_file = 'matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'override_dist_mtrx_notnum_rad1.csv'

        expected_output_file = 'test3k_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03l_dis_mtrx_merge(self):
        #
        #   Test 03l - Non-numeric values for column 'detec_radius2', expect that the original value is kept
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3l'  # Test folder name

        # File Names
        matrix_1_file = 'matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'override_dist_mtrx_notnum_rad2.csv'

        expected_output_file = 'test3l_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_03m_dis_mtrx_merge(self):
        #
        #   Test 03m - one null value in detect column, no expected change for that record
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3m'  # Test folder name

        # File Names
        matrix_1_file = 'matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'override_dist_mtrx_null_rad2.csv'

        output_matrix_file = 'matched_detections_2013_distance_matrix_merged.csv'
        expected_output_file = 'test3m_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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

    def test_03n_dis_mtrx_merge(self):
        #
        #   Test 03n - no expected changes
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3n'  # Test folder name

        # File Names
        matrix_1_file = 'matched_detections_2013_distance_matrix_no_change_rec3.csv'
        matrix_2_file = 'override_dist_mtrx_no_change_rec3.csv'

        output_matrix_file = 'matched_detections_2013_distance_matrix_no_change_rec3_merged.csv'
        expected_output_file = 'test3n_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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

    def test_03o_dis_mtrx_merge(self):
        #
        #   Test 03o - first file is full
        #              second file is missing column names
        #
        from common_python import dis_mtrx_merge

        fldr = 'test3o'  # Test folder name

        # File Names
        matrix_1_file = 'matched_detections_2013_distance_matrix.csv'
        matrix_2_file = 'override_dist_mtrx.csv'

        output_matrix_file = 'matched_detections_2013_distance_matrix_merged.csv'
        expected_output_file = 'test3o_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_1_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              matrix_2_file), DATA_PATH)

        # Run the load_detections function on the test file
        dis_mtrx_merge.dis_mtx_merge(reqcode='reqmerge',
                                     distance_matrix_input=matrix_1_file,
                                     distance_real_input=matrix_2_file,
                                     data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output
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
        from common_python import uniqueid

        fldr = 'test4'  # Test folder name

        # File Names
        detection_file = 'test4_detections.csv'
        output_unique_file = 'test4_detections_unqid.csv'
        expected_output_file = 'test4_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the detection file into the test data directory
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)

        # Run the load_detections function on the test file
        uniqueid.add_column_unqdetecid(detection_file, DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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
        from common_python import uniqueid

        fldr = 'test4a'  # Test folder name

        # File Names
        detection_file = 'test4a_detections.csv'
        output_unique_file = 'test4a_detections_unqid.csv'
        expected_output_file = 'test4a_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the filter step into the testing folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)

        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              output_unique_file), DATA_PATH)

        # Run the uniqueid function which will fail due to the output already existing
        uniqueid.add_column_unqdetecid(detection_file, DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Assertions 
        # Console output
        self.assertMultiLineEqual(output, expect_output)

    def test_04b_uniqueid(self):
        #
        #    TEST 4b - run uniqueid function when the unqdetecid column already exists
        #
        from common_python import uniqueid

        fldr = 'test4b'  # Test folder name

        # File names
        detection_file = 'test4b_detections_unqid.csv'
        expected_output_file = 'test4b_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the detection file into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)

        # Run the uniqueid function. add_column_unqdetecid is expected to fail
        # because unqdetecid column already exists
        uniqueid.add_column_unqdetecid(detection_file, DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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
        from common_python import compress

        fldr = 'test5'  # Test folder name

        # File names
        detection_file = 'test5_detections.csv'
        output_compressed_file = 'test5_detections_compressed_detections_v00.csv'
        expected_output_file = 'test5_expected_output.txt'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the detection file into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              detection_file), DATA_PATH)

        # Execute the compression function
        compress.CompressDetections(detection_file, DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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
        from common_python import cohorts

        fldr = 'test6'  # Test folder name

        # File Names
        compressed_file = 'test6_compressed_detections.csv'
        expected_output_file = 'test6_expected_output.txt'
        output_cohort_file = 'test6_compressed_detections_cohort_60min.csv'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files needed for the cohort step into the test data folder
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              compressed_file), DATA_PATH)

        # Execute the cohort function with 60 minute interval time
        cohorts.CohortRecords(interval_time=60,
                              compressed_file=compressed_file,
                              data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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

    def test_06a_cohorts(self):
        #
        #    TEST 6a - cohort: missing input file
        #
        from common_python import cohorts

        fldr = 'test6a'  # Test folder name

        # File Names
        compressed_file = 'missing_compressed_file.csv'
        expected_output_file = 'test6a_expected_output.txt'

        stdout = CaptureStdout() # Capture console output to compare to what is expected

        # Execute the cohort function with 60 minute interval time
        cohorts.CohortRecords(interval_time=60,
                              compressed_file=compressed_file,
                              data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

        # Read expected output into a string
        expect_output = open(path.join(TESTFILE_PATH, fldr,
                                       expected_output_file)).read()

        # Console output assertions
        self.assertMultiLineEqual(output, expect_output)

    def test_07_conversion(self):
        #
        #    TEST 7 - Test using an ANSI windows-1252 format. Loading steps fails 
        #                unless file is converted using the conversion module.
        #
        from common_python import conversion
        from common_python import load_detections

        fldr = 'test7'  # Test folder name

        # File Names
        input_detect_file = 'test7_detections.csv'
        expected_output_file = 'test7_expected_output.txt'
        output_converted_file = 'test7_detections_utf8.csv'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

        # Copy the testing files
        shutil.copy(path.join(TESTFILE_PATH, fldr,
                              input_detect_file), DATA_PATH)

        # Execute the load_detection function to get expected failure
        load_detections.loadDetections(detection_file=input_detect_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)

        # Run the utf-8 conversion function on the windows-1252 formatted file
        conversion.conversion(input_detect_file, data_dir=DATA_PATH)

        # Execute the same loading function with the converted file which is now 
        # expected to pass
        load_detections.loadDetections(detection_file=output_converted_file,
                                       version_id='00',
                                       DistanceMatrix=False,
                                       ReloadInputFile=True,
                                       SuspectDetections=False,
                                       time_interval='60',
                                       detection_radius='',
                                       data_directory=DATA_PATH)

        # Release console output
        output = stdout.release_output()  # Release output

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
        from common_python import interval_data_tool

        fldr = 'test8'  # Test folder name

        # File Names
        input_detect_file = 'test8_detections.csv'
        input_dist_mtrx_file = 'test8_distance_matrix.csv'
        expected_output_file = 'test8_expected_output.txt'
        output_interval_file = 'test8_detections_interval_data_v00.csv'
        output_compressed_file = 'test8_detections_compressed_detections_v00.csv'

        # Capture console output to compare to what is expected
        stdout = CaptureStdout()

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
        output = stdout.release_output()  # Release output

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

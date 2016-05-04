import datetime
import unittest
import sandbox_use_testing
from StringIO import StringIO
from os import path

SCRIPT_PATH = path.dirname( path.abspath(__file__) )
OUTPUT_PATH = path.join(SCRIPT_PATH, 'test_output')

if __name__ == '__main__':
    # USE TEST RUNNING
    
    # Use the current date in log file name
    d = datetime.datetime.now()
    d.strftime("use_testing_%Y_%m_%dT%H%M.csv")
    
    # Create the log file and open for write 
    log_file = path.join(OUTPUT_PATH, d.strftime("use_testing_%Y_%m_%dT%H%M.txt"))
    f = open(log_file, "w")
    
    # Run the sandbox_use_testing unittests
    runner = unittest.TextTestRunner(stream=f, verbosity=2)
    runner.run(unittest.makeSuite(sandbox_use_testing.TestSandbox))
    f.close()
    
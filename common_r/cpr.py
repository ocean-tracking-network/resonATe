import sys
import os

CPR_SCRIPT_PATH = os.path.dirname( os.path.abspath(__file__) )
PYTHON_PATH = os.path.join(CPR_SCRIPT_PATH,os.pardir,'common_python')

def common_python_runner(_file="", mod="",func="", *arg):
  # Runs functions located in the common python library path
  #print 'file:{}\nmodule:{}\nfunction:{}\nnum_of_args={}'.format(_file,mod,func,len(arg))
  def detect_bool(input):
    if input == 'TRUE':
        return True
    elif input == 'FALSE':
        return False
    return input
  
  arguments = arg
  arguments = map(detect_bool, arguments)
  
  sys.path.append(PYTHON_PATH)
  i = __import__(mod)
  
  func = getattr(i, func, None)
  
  func(*arguments)

common_python_runner(*sys.argv)

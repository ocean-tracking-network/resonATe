

cleanup <- function(){
  library(rPython,quietly=TRUE)
  
  # Load load_detections module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'',getwd(),'\')',sep=''))
  python.exec("import common_python.cleanup")
  python.exec("reload(common_python.cleanup)")
  
  # Run the cleanup script
  main <- python.call('common_python.cleanup.cleanup',
                      'reqcleanup')
}
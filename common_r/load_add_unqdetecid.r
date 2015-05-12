setwd("/home/sandbox/RStudio/sandbox")

add_column_unqdetecid <- function(input_file){
  library(rPython,quietly=TRUE)
  
  # Load load_detections module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'',getwd(),'\')',sep=''))
  python.exec("import common_python.uniqueid")
  python.exec("reload(common_python.uniqueid)")
  
  # Run the cleanup script
  main <- python.call('common_python.uniqueid.add_column_unqdetecid',
                      input_file)
}
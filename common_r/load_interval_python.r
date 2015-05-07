setwd("/home/sandbox/RStudio/sandbox")

intervalData <- function(){
  # Load rPyton and set the working directory
  library(rPython,quietly=TRUE)
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'',getwd(),'\')',sep=''))
  
  # Load interval data tool
  python.exec("import common_python.interval_data_tool")
  python.exec("reload(common_python.interval_data_tool)")
  
  # Run the interval data script
  main <- python.call("common_python.interval_data_tool.intervalData",detection_file, distance_matrix)
}
intervalData <- function(){
  # Load rPyton and set the working directory
  library(rPython,quietly=TRUE)
  setwd("/home/sandbox/RStudio/sandbox")
  python.exec("import sys, os")
  python.exec("sys.path.append('/home/sandbox/RStudio/sandbox')")
  python.exec("import common_python.interval_data_tool")
  
  # Run the interval data script
  main <- python.call("common_python.interval_data_tool.intervalData",detection_file, distance_matrix)
}
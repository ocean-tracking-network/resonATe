convert_file <- function(input_file){
  # Load rPyton and set the working directory
  library(rPython,quietly=TRUE)
  setwd("/home/sandbox/RStudio/sandbox")
  
  python.exec("import sys, os")
  python.exec("sys.path.append('/home/sandbox/RStudio/sandbox')")
  python.exec("import common_python.conversion")
  
  if(!exists("input_encoding")){input_encoding <- NaN}
  
  # Run the conversion script
  main <- python.call("common_python.conversion.conversion",input_file, input_encoding)
}


convert_file <- function(input_file){
  library(rPython,quietly=TRUE)
  
  # Load conversion module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'',getwd(),'\')',sep=''))
  python.exec("import common_python.conversion")
  python.exec("reload(common_python.conversion)")
  
  # Run the conversion script
  main <- python.call('common_python.conversion.conversion',
                      input_file)
}
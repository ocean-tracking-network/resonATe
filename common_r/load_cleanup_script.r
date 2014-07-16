cleanup <- function(){
  # Load rPyton and set the working directory
  library(rPython,quietly=TRUE)
  setwd("/home/sandbox/RStudio/sandbox")
  
  python.exec("import sys, os")
  python.exec("sys.path.append('/home/sandbox/RStudio/sandbox')")
  python.exec("import common_python.cleanup")
  
  # Run the cleanup script
  main <- python.call("common_python.cleanup.cleanup","reqcleanup")
}


compress_detections <- function(detection_file){
  # Load rPython module
  library(rPython,quietly=TRUE)
  
  # Load compression module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'', getwd(), '\')',sep=''))
  python.exec("import common_python.compress")
  python.exec("reload(common_python.compress)")
  
  # Run the compression script
  main <- python.call('common_python.compress.CompressDetections',
                      detection_file)
}
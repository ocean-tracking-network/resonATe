setwd("/home/sandbox/RStudio/sandbox")

loadDistanceMerge <- function(reqcode, distance_matrix_input, distance_real_input){
  library(rPython,quietly=TRUE)
  
  # Load dis_matrix_merge module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'',getwd(),'\')',sep=''))
  python.exec("import common_python.dis_mtrx_merge")
  python.exec("reload(common_python.dis_mtrx_merge)")
  
  # Run the merge script
  main <- python.call('common_python.dis_mtrx_merge.dis_mtx_merge',
                      reqcode,distance_matrix_input, distance_real_input)
                  
}

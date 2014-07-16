library(rPython)
python.exec("import sys, os")
python.exec("sys.path.append('/home/sandbox/RStudio/sandbox')")
python.exec("import common_python.dis_mtrx_merge as dis")
setwd("/home/sandbox/RStudio/sandbox")

loadDistanceMerge <- function(){
  #reload the python script into memory
  #python.exec("reload(dis)")
  
  #Run the loading script
  python.call("dis.dis_mtx_merge",reqcode=reqcode,distance_matrix_input=distance_matrix_input,distance_real_input=distance_real_input)
}

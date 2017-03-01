loadDistanceMerge <- function(reqcode, distance_matrix_input, distance_real_input){
  # Run the merge script
                  
  out = system2("/opt/anaconda/bin/python", 
                stdout = TRUE, stderr = TRUE, 
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","dis_mtrx_merge","dis_mtx_merge",
                          paste("'",reqcode,"'",sep=''),
                          paste("'",distance_matrix_input,"'",sep=''),
                          paste("'",distance_real_input,"'",sep='')))
  for (line in out){
    print(line)
  }
}



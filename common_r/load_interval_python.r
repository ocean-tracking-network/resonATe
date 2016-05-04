
intervalData <- function(){
  # Run the interval data script
  out = system2("/opt/anaconda/bin/python", 
                stdout = TRUE, stderr = TRUE, 
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","interval_data_tool","intervalData",
                          paste("'",detection_file,"'",sep=''),
                          paste("'",distance_matrix,"'",sep='')))
  for (line in out){
    print(line)
  }
  
}


compress_detections <- function(detection_file){
  # Run the compression script
  out = system2("/opt/anaconda/bin/python", 
                stdout = TRUE, stderr = TRUE, 
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","compress","CompressDetections",
                          paste("'",detection_file,"'",sep='')))
  for (line in out){
    print(line)
  }
}


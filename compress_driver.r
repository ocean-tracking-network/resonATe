################ Libraries ###################
source("/home/sandbox/RStudio/sandbox/common_r/load_compression_script.r") # Load conversion function

################ User Input ################
detection_file <- 'detections.csv'

################ Create compression file ################
compress_detections( detection_file)

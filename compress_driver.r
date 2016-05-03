################ Libraries ###################
setwd("~/otn-toolbox")
source("./common_r/load_compression_script.r") # Load conversion function

################ User Input ################
detection_file <- 'acs_matched_detections_2012.csv'

################ Create compression file ################
compress_detections( detection_file)

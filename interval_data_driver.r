################ Libraries ###################
setwd("~/otn-toolbox")
source("./common_r/load_interval_python.r")

################ User Input ################
detection_file <- 'detections.csv' #Detection file input name
distance_matrix <-'detections_distance_matrix_v00.csv' #Distance matrix file input name

################ Interval Processing Functions ################
intervalData() #Creates the compressed detections and interval data files
################ Libraries ###################
setwd("~/otn-toolbox")
source("./common_r/load_cohort_script.r") # Load conversion function

################ User Input ################
time_interval <- 60
# compressed file created from running the interval data or the compression tool.
compressed_file <- 'compressed_detections.csv' 

################ Create cohort file ################
cohort_records( time_interval, compressed_file )


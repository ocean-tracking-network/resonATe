################ Libraries ###################
setwd("~/otn-toolbox")
source("./common_r/load_conversion_script.r")  # Load conversion function

################ User Input ################
input_file <- 'detections.csv' # used by convert_file() function

################ Convert input_file into UTF8 ################
convert_file( input_file ) # converts the input_file to utf8
################ Libraries ###################
#set current working directory
setwd("/home/sandbox/RStudio/sandbox")
source("common_r/load_dis_merge_python.r")

################ User Input ################
reqcode <- 'reqmerge' #request code for merge two station matrix files
distance_matrix_input <-   'matrix.csv' # first file will be the full file
distance_real_input <- 'matrix_update.csv' # second file is a set of distances which are to be used to override the distances on the first file

################ Function Merge Real_distance for Station Matrix ################
# load two detections files
# Merger real_distance in file 1 from file 2

loadDistanceMerge(reqcode, distance_matrix_input, distance_real_input)

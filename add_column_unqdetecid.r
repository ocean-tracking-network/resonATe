################ Libraries ###################
#set current working directory
setwd("/home/sandbox/RStudio/sandbox")
source("common_r/load_add_unqdetecid.r")

################ User Input ################
input_file <- 'example_detections.csv'# Input file, must not contain the unqdetecid column.

################ Create file with unqdetecid ################
add_column_unqdetecid(input_file)

setwd("/home/sandbox/RStudio/sandbox")

cohort_records <- function(time_interval, compressed_file){
  # Load rPython module
  library(rPython,quietly=TRUE)
  
  # Load load_detections module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'', getwd(), '\')',sep=''))
  python.exec("import common_python.cohorts")
  python.exec("reload(common_python.cohorts)")
  
  # Run the cohort creation script
  main <- python.call('common_python.cohorts.CohortRecords',
                      time_interval, compressed_file)
}
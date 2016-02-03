

cohort_records <- function(time_interval, compressed_file){
  # Load rPython module
  library(rPython,quietly=TRUE)
  
  # Load load_detections module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'', getwd(), '\')',sep=''))
  python.exec("import common_python.cohorts")
  python.exec("reload(common_python.cohorts)")
  
  # Check for int values
  check.integer <- function(N){
    !length(grep("[^[:digit:]]", as.character(N)))
  }
  
  # Only execute if the time value is an integer
  if (check.integer(time_interval)){
    # cast to int, removing any precision 
    time_interval <- as.integer(time_interval)
    
    # Run the cohort creation script
    main <- python.call('common_python.cohorts.CohortRecords',
                        time_interval, compressed_file)
  }
  else{
    return("Please enter an integer value for time_interval.")
  }
}
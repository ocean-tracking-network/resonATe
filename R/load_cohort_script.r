cohort_records <- function(time_interval, compressed_file){
  # Check for int values
  check.integer <- function(N){
    !length(grep("[^[:digit:]]", as.character(N)))
  }
  
  # Only execute if the time value is an integer
  if (check.integer(time_interval)){
    # cast to int, removing any precision 
    time_interval <- as.integer(time_interval)
    
    # Run the cohort creation script
    out = system2("/opt/anaconda/bin/python", 
                  stdout = TRUE, stderr = TRUE, 
                  args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","cohorts","CohortRecords",
                            paste("'",time_interval,"'",sep=''),
                            paste("'",compressed_file,"'",sep='')))
    for (line in out){
      print(line)
    }
  }
  else{
    return("Please enter an integer value for time_interval.")
  }
}


add_column_unqdetecid <- function(input_file){
  # Check for global variables/set defaults
  if(!exists("detection_file")){detection_file <<- ''}
  if(!exists("input_version_id")){input_version_id <<- ''}
  if(!exists("time_interval")){time_interval <<- 60}
  if(!exists("SuspectDetections")){SuspectDetections <<- FALSE}
  if(!exists("DistanceMatrix")){DistanceMatrix <<- FALSE}
  if(!exists("ReloadInputFile")){ReloadInputFile <<- FALSE}
  if(!exists("detection_radius")){detection_radius <<- ''}
  
  out = system2("/opt/anaconda/bin/python", 
                stdout = TRUE, stderr = TRUE, 
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","uniqueid","add_column_unqdetecid",
                          paste("'",input_file,"'",sep='')))
  for (line in out){
    print(line)
  }
}
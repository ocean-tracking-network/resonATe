loadDetections <- function(){
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
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","load_detections","loadDetections",
                          paste("'",detection_file,"'",sep=''),
                          paste("'",input_version_id,"'",sep=''), 
                          paste("'",DistanceMatrix,"'",sep=''),
                          paste("'",ReloadInputFile,"'",sep=''), 
                          paste("'",SuspectDetections,"'",sep=''), 
                          paste("'",time_interval,"'",sep=''),
                          paste("'",detection_radius,"'",sep='')))
  for (line in out){
    print(line)
  }
}

filterDetections <- function(){
  # Check for global variables/set defaults
  if(!exists( "input_version_id" )){input_version_id <<- ''}
  if(!exists( "detection_file" )){detection_file <<- ''}
  if(!exists( "SuspectFile" )){SuspectFile <<- FALSE}
  if(!exists( "OverrideSuspectDetectionFile" )){OverrideSuspectDetectionFile <<- FALSE}
  if(!exists( "DistanceMatrix" )){DistanceMatrix <<- FALSE}
  if(!exists( "ReloadInputFile" )){ReloadInputFile <<- FALSE}
  if(!exists("detection_radius")){detection_radius <<- ''}
  
  out = system2("/opt/anaconda/bin/python", 
                stdout = TRUE, stderr = TRUE, 
                args=list("/home/vagrant/otn-toolbox/common_r/cpr.py","filter_detections","filterDetections",
                          paste("'",detection_file,"'",sep=''),
                          paste("'",input_version_id,"'",sep=''), 
                          paste("'",SuspectFile,"'",sep=''),
                          paste("'",OverrideSuspectDetectionFile,"'",sep=''), 
                          paste("'",DistanceMatrix,"'",sep=''), 
                          paste("'",detection_radius,"'",sep=''),
                          paste("'",ReloadInputFile,"'",sep='')))
  for (line in out){
    print(line)
  }
}
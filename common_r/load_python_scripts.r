setwd("/home/sandbox/RStudio/sandbox")

loadDetections <- function(){
  library(rPython,quietly=TRUE)

  # Load load_detections module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'',getwd(),'\')',sep=''))
  python.exec("import common_python.load_detections")
  python.exec("reload(common_python.load_detections)")
  
  # Check for global variables/set defaults
  if(!exists("detection_file")){detection_file <<- ''}
  if(!exists("input_version_id")){input_version_id <<- ''}
  if(!exists("time_interval")){time_interval <<- 60}
  if(!exists("SuspectDetections")){SuspectDetections <<- FALSE}
  if(!exists("DistanceMatrix")){DistanceMatrix <<- FALSE}
  if(!exists("ReloadInputFile")){ReloadInputFile <<- FALSE}
  if(!exists("detection_radius")){detection_radius <<- ''}
  
  # Run the loading script
  main <- python.call('common_python.load_detections.loadDetections',
                      detection_file,input_version_id, DistanceMatrix,
                      ReloadInputFile, SuspectDetections, time_interval,
                      detection_radius)
}

filterDetections <- function(){
  library(rPython,quietly=TRUE)
  
  # Load filter_detections module
  python.exec("import sys, os")
  python.exec(paste('sys.path.append(\'',getwd(),'\')',sep=''))
  python.exec("import common_python.filter_detections")
  python.exec("reload(common_python.filter_detections)")
  
  # Check for global variables/set defaults
  if(!exists( "input_version_id" )){input_version_id <<- ''}
  if(!exists( "detection_file" )){detection_file <<- ''}
  if(!exists( "SuspectFile" )){SuspectFile <<- FALSE}
  if(!exists( "OverrideSuspectDetectionFile" )){OverrideSuspectDetectionFile <<- FALSE}
  if(!exists( "DistanceMatrix" )){DistanceMatrix <<- FALSE}
  if(!exists( "ReloadInputFile" )){ReloadInputFile <<- FALSE}
  if(!exists("detection_radius")){detection_radius <<- ''}
  
  main <- python.call('common_python.filter_detections.filterDetections',
                      detection_file,input_version_id, SuspectFile,
                      OverrideSuspectDetectionFile, DistanceMatrix,
                      detection_radius, ReloadInputFile)
}
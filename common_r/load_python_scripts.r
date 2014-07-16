library(rPython)
python.exec("import sys, os")
python.exec("sys.path.append('/home/sandbox/RStudio/sandbox')")
python.exec("import common_python.load_detections as ld")
python.exec("import common_python.filter_detections as fd")
setwd("/home/sandbox/RStudio/sandbox")

loadDetections <- function(){
  # Reload the python script into memory
  python.exec("reload(ld)")
  
  # Check for global variables/set defaults
  if(!exists("detection_file")){detection_file <<- ''}
  if(!exists("delimiter")){delimiter <<- ','}
  if(!exists("quotechar")){quotechar <<- '\\"'}
  if(!exists("input_version_id")){input_version_id <<- ''}
  if(!exists("encoding")){encoding <<- 'utf-8'}
  if(!exists("time_interval")){time_interval <<- 60}
  if(!exists("SuspectDetections")){SuspectDetections <<- FALSE}
  if(!exists("DistanceMatrix")){DistanceMatrix <<- FALSE}
  if(!exists("ReloadInputFile")){ReloadInputFile <<- FALSE}
  
  # Assign variables
  python.assign( "ld.time_interval", time_interval)
  python.assign( "ld.detection_file", detection_file)
  python.assign( "ld.delimiter", delimiter)
  python.assign( "ld.quotechar", quotechar)
  python.assign( "ld.version_id", input_version_id)
  python.assign( "ld.encoding", encoding)
  python.assign( "ld.SuspectDetections", SuspectDetections)
  python.assign( "ld.DistanceMatrix", DistanceMatrix)
  python.assign( "ld.ReloadInputFile", ReloadInputFile)
  
  #remove utf8 from single character variables
  python.exec("ld.delimiter = ld.delimiter.encode(\"utf8\")")
  python.exec("ld.quotechar = ld.quotechar.encode(\"utf8\")")
  
  # Run the loading script
  python.call("ld.loadDetections")
}

filterDetections <- function(){
  # Reload the python script into memory
  python.exec("reload(fd)")
  
  # Check for global variables/set defaults
  if(!exists( "input_version_id" )){input_version_id <<- ''}
  if(!exists( "detection_file" )){detection_file <<- ''}
  if(!exists( "delimiter" )){delimiter <<- ','}
  if(!exists( "quotechar" )){quotechar <<- '\\"'}
  if(!exists( "encoding" )){encoding <<- 'utf-8'}
  if(!exists( "SuspectFile" )){SuspectFile <<- FALSE}
  if(!exists( "OverrideSuspectDetectionFile" )){OverrideSuspectDetectionFile <<- FALSE}
  if(!exists( "DistanceMatrix" )){DistanceMatrix <<- FALSE}
  if(!exists( "ReloadInputFile" )){ReloadInputFile <<- FALSE}
  
  # Assign variables
  python.assign( "fd.version_id", input_version_id)
  python.assign( "fd.detection_file", detection_file)
  python.assign( "fd.delimiter", delimiter)
  python.assign( "fd.quotechar", quotechar)
  python.assign( "fd.encoding", encoding)
  python.assign( "fd.SuspectFile", SuspectFile)
  python.assign( "fd.DistanceMatrix", DistanceMatrix)
  python.assign( "fd.OverrideSuspectDetectionFile", OverrideSuspectDetectionFile)
  python.assign( "ld.ReloadInputFile", ReloadInputFile)
  
  # Run the filtering Script
  python.call("fd.filterDetections")
}
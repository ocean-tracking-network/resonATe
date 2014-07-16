################ Libraries ###################
#set current working directory
setwd("/home/sandbox/RStudio/sandbox")
source("common_r/load_python_scripts.r")

############### Switches ################
SuspectDetections  <- TRUE  # used by function loadDetections()
                     #TRUE will create list of suspect detections
                     #FALSE will not create a new file of suspect detections
DistanceMatrix  <- TRUE # used by functions loadDetections() and filterDetections()
                  #TRUE will create distance matrix
                  #FALSE will not create a new distance matrix file
OverrideSuspectDetectionFile <- FALSE # used by function filterDetections()
                               #FALSE will use the default file of suspect detections created from the loadDetections() step
                               #TRUE will use override file of suspect detections that you provide
ReloadInputFile <- FALSE    # used by function loadDetections()
                  #TRUE will always reload input detection file
                  #FALSE will use already loaded input detection file


################ User Input ################
detection_file <- 'detections.csv' #Detection file input name
input_version_id <- '00' #Version ID number [0 for initial(first) load]
time_interval <- '60' #Time interval used to evaluate suspect detections (in minutes)

################ Detection Processing Functions ################

################ Function Find Suspect Detections ################
#loads the detection input file into a database and optionally creates the suspect detection file and station distance matrix file
#To save time input file will not be reloaded if version id does not change. If your initial file has changed you need to rename it to get it to load

loadDetections() #message "loading complete" will appear when process is done

################  Function Filter Detections  ################
#returns a new detections file without the suspected detections which will have version id incremented
#uses as input file of detections and file of suspect detections creating in previous step
#will create a new distance matrix with version id incremented (if distance_matrix is set to TRUE)

if (OverrideSuspectDetectionFile == TRUE) {
  SuspectFile <- 'your override file name here.csv'
}
filterDetections() #message "filtering complete" will appear when process is done

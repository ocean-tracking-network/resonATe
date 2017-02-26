library(dplyr)
library(lubridate)
library(tidyr)

filterDetections <- function(detection_file,
                             suspect_file=NULL,  # TODO: deal w/ supplied suspect detfiles
                             detection_radius=NULL, 
                             min_time_buffer=60, 
                             distance_matrix=F)
{
  
  mandatory_columns <- c('station', 'unqdetecid', 'datecollected', 'catalognumber')
  dat <- read.csv(detection_file)
  
  if(all(mandatory_columns %in% names(dat))) # if we have all column names.
  {
    # get unique individuals
    anm <- dat %>% distinct(catalognumber)
    dat <- dat %>% mutate(
      datecollected = parse_date_time(datecollected, "%Y-%m-%d %H:%M:%S")
    )
    
    out <- dat %>% 
      group_by(catalognumber) %>% 
      arrange(datecollected) %>%
      mutate(
        last.date = lag(datecollected),
        this.date = datecollected,
        next.date = lead(datecollected),
        
        last.diff = suppressWarnings(difftime(this.date, last.date, units="mins")),
        next.diff = suppressWarnings(difftime(next.date, this.date, units="mins"))
      ) %>%  # now need to make the first/last detection calc not-NA and not-true, evaluate only if other side within timebounds.
      replace_na(list(last.diff=min_time_buffer+1, next.diff=min_time_buffer+1)
      ) %>% # Now can run the filter step to evaluate
      mutate(
        filter.passed = last.diff <= min_time_buffer | next.diff <= min_time_buffer
      ) 
  }
  # Subset based on the value of filter.passed
  good <- subset(out, filter.passed)
  susp <-subset(out, !filter.passed)
  if (!distance_matrix){
    return(list("filtered" = good, "suspect" = susp))
  }
  else # dist_mtrx required. Takes a long time!
  {
    library(geosphere) # Only need this if we're making a distmatrix
    # TODO: Verify we only want the acceptable filtered stations here?
    stations <- good %>% select(station, latitude, longitude) %>% distinct
    # distances are in metres, dividing to get km.
    mat <- distm(stations[,c('longitude','latitude')], fun=distVincentyEllipsoid) / 1000
    rownames(mat) <- stations$station
    colnames(mat) <- stations$station
    return(list("filtered" = good, "suspect" = susp, "dist_mtrx" = mat))
  }
}

# Testing functionality of the defined functions above.

# Just Filtering:
dat <- read.csv('~/data/nsbs_matched_detections_2015.csv')
out <- filterDetections('~/data/nsbs_matched_detections_2015.csv')
filtered <- out$filtered
susp <- out$suspect
# Filter w/ Distance Matrix
mtrx_out <-filterDetections('~/data/nsbs_matched_detections_2015.csv', distance_matrix=T)

# Known Issues:
# DB filtration from old toolbox used to also flag the release locations

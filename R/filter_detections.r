#' Temporal Filter Tool
#'
#' This function filters out acoustic detections that are isolated by more than N minutes on either side
#' @param detection_df A dataframe read from a CSV file of detections
#' @param suspect_df A dataframe of suspect detections from a previous or different filter run (not yet implemented)
#' @param detection_radius A detection radius. (not used)
#' @param min_time_buffer How far from other detections a detection must be to be filtered (in minutes)
#' @param distance_matrix Whether or not to generate a distance matrix from the supplied station locations.
#' @keywords acoustic telemetry filter temporal
#' @export
#' @examples
#' filter_detections(read.csv('my-detection-file.csv'))
#' filter_detections(read.csv('my-detection-file.csv), min_time_buffer=30, distance_matrix=T)

library(dplyr)
library(lubridate)
library(tidyr)

filter_detections <- function(detection_df,
                              suspect_df=NULL,  # TODO: deal w/ supplied suspect det frames? Or just let people filter out their own stuff.
                              detection_radius=NULL, 
                              min_time_buffer=60, 
                              distance_matrix=F)
{
  
  mandatory_columns <- c('station', 'unqdetecid', 'datecollected', 'catalognumber', 'latitude', 'longitude')
  dat <- detection_df
  
  if(all(mandatory_columns %in% names(dat))) # if we have all column names.
  {
    # get unique individuals
    anm <- dat %>% distinct(catalognumber)
    dat <- dat %>% mutate(
      datecollected = parse_date_time(datecollected, "%Y-%m-%d %H:%M:%S")
    )
    
    # Calculate the temporal filter result for each detection.
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
    
    # Subset based on the value of filter.passed
    good <- subset(out, filter.passed)
    susp <- subset(out, !filter.passed)
    
    if (!distance_matrix){
      return(list("filtered" = good, "suspect" = susp))
    }
    else # dist_mtrx required. Takes a long time!
    {
      # only really need lat/lon in here. Could do rest of calc w/o it.
      library(geosphere) # Only need this lib if we're making a distmatrix
      # TODO: Verify we only want the acceptable filtered stations here?
      stations <- good %>% select(station, latitude, longitude) %>% distinct
      # distances are in metres, dividing to get km.
      mat <- distm(stations[,c('longitude','latitude')], fun=distVincentyEllipsoid) / 1000
      rownames(mat) <- stations$station
      colnames(mat) <- stations$station
      return(list("filtered" = good, "suspect" = susp, "dist_mtrx" = mat))
    }
  }
  else
  {
    # TODO: raise an exception in R-land.
  }
}

# Known Issues:
# DB filtration from old toolbox used to also flag the release locations

#' Compressed Detection Dataframe
#'
#' This function compresses concurrent detections of a tag at a single station into an aggregate w/ simple statistics
#' @param detection_df A dataframe read from a CSV file of detections
#' @keywords acoustic telemetry compress temporal
#' @export
#' @examples
#' compress_detections(read.csv('my-detection-file.csv'))

library(dplyr)


compress_detections <- function(detection_df)
{
  # Takes a dataframe of detections and compresses concurrent detections at a single station.
  mandatory_columns <- c('unqdetecid', 'datecollected', 'catalognumber', 'station')
  
  # TODO: cast datecollected as datetime?
  
  if(all(mandatory_columns %in% names(detection_df))) # if we have all column names.
  {
    # # Can't guarantee they've sorted everything by catalognumber (animal ID) in the input file.
    detection_df <- detection_df %>% arrange(catalognumber, datecollected, station)
    
    # Calculate the order of detection groups for each animal and write it as seq_num
    groups <- detection_df %>% group_by(catalognumber) %>%
              arrange(catalognumber, datecollected) %>%
              mutate(seq_num = cumsum(ifelse(station != lag(station) | is.na(lag(station)), 1, 0)))
    
    # Now seq_num is set. Group-by it, and calculate the stats for each group.
    
    stat_df <- groups %>% group_by(catalognumber, seq_num, station) %>%
               arrange(catalognumber, datecollected) %>%
               summarize(total_count=length(unqdetecid),
                         startunqdetecid=first(unqdetecid),
                         endunqdetecid=last(unqdetecid),
                         startdate=min(datecollected),
                         enddate=max(datecollected), 
                         avg_time_between_det=(enddate - startdate) / 60 / max(total_count -1, 1))
    
    return(stat_df)
  }
  else
  {
    # TODO: raise an exception in R-land.
    print('whoops')
  }
}

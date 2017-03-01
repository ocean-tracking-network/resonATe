#' Add Unique Detection ID
#'
#' Adds an explicit incremental integer index column to a dataframe for compatibility with other functionality
#' @param df A dataframe with no duplicate rows
#' @keywords add id unique
#' @export
#' @examples
#' df <- add_column_unqdetecid(df)
#' filtered_df <- filter_detections(add_column_unqdetecid('my-unindexed-detections.csv'))

add_column_unqdetecid <- function(df){
  df <- df %>% mutate(unqdetecid = row_number())
  return(df)
}

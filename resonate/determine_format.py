import pandas as pd


def detect(dataframe: pd.DataFrame) -> dict:
    formats = [
        {
            "col_datecollected": "dateCollectedUTC",
            "col_unique_id": "unqDetecID",
            "col_scientificname": "scientificName",
            "col_longitude": "decimalLongitude",
            "col_latitude": "decimalLatitude",
            "col_station": "station",
            "col_catalognumber": "catalogNumber",
            "col_fieldnumber": "tagName",
        },
        {
            "col_datecollected": "datecollected",
            "col_unique_id": "unqdetecid",
            "col_scientificname": "scientificname",
            "col_longitude": "longitude",
            "col_latitude": "latitude",
            "col_station": "station",
            "col_catalognumber": "catalognumber",
            "col_fieldnumber": "fieldnumber",
        },
        # add some subsets for functions that use less columns
        # datecollected``, ``catalognumber``, ``station``, ``latitude``, and ``longitude`
        {   "col_datecollected": "dateCollectedUTC",
            "col_longitude": "decimalLongitude",
            "col_latitude": "decimalLatitude",
            "col_station": "station",
            "col_catalognumber": "catalogNumber"},
        {   "col_datecollected": "datecollected",
            "col_longitude": "longitude",
            "col_latitude": "latitude",
            "col_station": "station",
            "col_catalognumber": "catalognumber"}
    ]

    columns = dataframe.columns
    for format in formats:
        # check for matching set of column names
        if set(format.values()).issubset(set(columns)):
            return format

Subsetting Data
===============

Sometimes there is too much data for a visualization tool to handle, or
you wish to only take a certain subset of your input data and apply it
elsewhere.

These examples, written in Python and leveraging the Pandas data
manipulation package, are meant as a starting point. More complex
operations are possible in Pandas, but these should form a baseline of
understanding that will cover the most common operations.

.. code:: python

    import pandas as pd
    filename = "/path/to/data.csv"
    data = pd.read_csv(directory+filename)

Subsetting data by date range
-----------------------------

Provide a date field, as well as starting and ending date range. By
default, the detection date column of a detection extract file is
provided.

.. code:: python

    # Enter the column name that contains the date you wish to evaluate
    datecol = 'datecollected'
    # Enter the start date in the following format
    startdate = "YYYY-MM-DD"
    
    # Enter the end date in the following format
    enddate = "YYYY-MM-DD"
    
    # Subsets the dat between the two indicated dates uding the datecollected column
    data_date_subset = data[(data[datecol] > startdate) & (data[datecol] < enddate)]
    
    # Output the subset data to a new CSV in the indicated directory
    data_date_subset.to_csv(directory+startdate+"_to_"+enddate+"_"+filename, index=False)

Subsetting on column value
--------------------------

Provide the column you expect to have a certain value and the value
you’d like to create a subset from.

.. code:: python

    # Enter the column you want to subset
    column=''
    
    # Enter the value you want to find in the above column
    value=''
    
    # The following pulls the new data subset into a Pandas DataFrame
    data_column_subset=data[data[column]==value]
    
    # Output the subset data to a new CSV in the indicated directory
    data_column_subset.to_csv(directory+column+"_"+value.replace(" ", "_")+"_"+filename, index=False)


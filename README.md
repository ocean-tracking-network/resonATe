resonATe
========

resonATe is the Ocean Tracking Network's acoustic telemetry analysis toolkit.
It can be used to filter, compress, visualize and analyze acoustic detection
extracts from OTN and other marine telemetry data.



* [Abacus Plot](#abacus-plot)
* [Bubble Plot](#bubble-plot)
* [Cohort](#cohort)
* [Compress Detections](#compressing-detections)
* [Distance Matrix](#distance-matrix)
* [Filtering](#filtering)
* [Interval Data](#interval-data)
* [Residence Index](#residence-index)
* [Unique ID](#unique-id)
* [Visual Timeline](#visual-timeline)


Abacus Plot
-----------

The abacus plot is a way to plot annimal along time. The function uses Plotly to place your points on a scatter plot. ``ycolumn`` is used as the y axis and ``datecollected`` is used as the x axis. ``color_column`` is used to group detections together and assign them a color.



Bubble Plot
-----------

The bubble plot function returns a Plotly scatter plot layered ontop of a map. The color of the markers will indicate the number of detections at each location. Alternatively, you can indicate the number of individuals seen at each location by using ``type = 'individual'``.



Cohort
------

The tool takes a file of compressed detections and a time parameter in minutes. It identifies groups of animals traveling together. Each station an animal visits is checked for other animals detected there within the specified time period.



Compressing Detections
----------------------

Compressing detections is done by looking at the detection times and locations of an animal. Any detections that occur successively in time, in the same location are combined into a single detection with a start and end time. The result is a compressed detections Pandas DataFrame.

Compression is the first step of the Mihoff Interval Data Tool. Compressed detection DataFrames are needed for the tools, such as interval and cohort.



Filtering
---------

*(White, E., Mihoff, M., Jones, B., Bajona, L., Halfyard, E. 2014. White-Mihoff False Filtering Tool)*


OTN has developed a tool which will assist with filtering false detections. The first level of filtering involves identifying isolated detections. The original concept came from work done by Easton White. He was kind enough to share his research database with OTN. We did some preliminary research and developed a proposal for a filtering tool based on what Easton had done. This proof of concept was presented to Steve Kessel and Eddie Halfyard in December 2013 and a decision was made to develop a tool for general use.

This is a very simple tool. It will take an input file of detections and based on an input parameter will identify suspect detections. The suspect detections will be put into a dataframe which the user can examine. There will be enough information for each suspect detection for the user to understand why it was flagged. There is also enough information to be able to reference the detection in the original file if the user wants to see what was happening at the same time.

The input parameter is a time in minutes. We used 3600 seconds as the default as this is what was used in Easton's code. This value can be changed by the user. The output contains a record for each detection for which there has been more than xx minutes since the previous detection (of that tag/animal) and more than the same amount of time until the next detection. It ignores which receiver the detection occurred at. That is all it does, nothing more and nothing less.


Distance Matrix
---------------

This takes a DataFrame created by the White-Mihoff False Filtering tool. The file contains rows of station pairs with the straight line distance between them calculated in metres. A station pair will only be in the file if an animal traveled between the stations. If an animal goes from stn1 to stn2 and then to stn3, pairs stn1-stn2 and stn2-stn3 will be in the file. If no animal goes between stn1 and stn3, that pair will not be in the file. The tool also takes a file that the researcher provides of ‘real distances’.  The output will be a file which looks like the first file with the ‘real distance’ column updated.


Interval Data
--------------------

*(Mihoff, M., Jones, B., Bajona, L., Halfyard, E. 2014. Mihoff Interval Data Tool)*

This tool will take a DataFrame of compressed detections and a distance matrix and output an interval DataFrame. The Interval DataFrame will contain records of the animal id, the arrival time at stn1, the departure time at stn1, the detection count at stn1, the arrival time at stn2, time between detections at the two stations, the interval in seconds, the distance between stations, and the velocity of the animal in m/s.



Residence Index
---------------

This residence index tool will take a compressed or uncompressed detection file and caculate the residency index for each station/receiver in the detections. A CSV file will be written to the data directory for future use. A Pandas DataFrame is returned from the function, which can be used to plot the information. The information passed to the function is what is used to calculate the residence index, make sure you are only passing the data you want taken into consideration for the residence index (i.e. species, stations, tags, etc.).



Unique Id
---------

This tool will add a column to any file. The unique id will be sequential integers. No validation is done on the input file.


Visual Timeline
---------------

This tool takes a detections extract file, compresses it, and generates an HTML and JSON file to an ``html`` folder.

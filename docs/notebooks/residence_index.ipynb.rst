Residence Index
===============

Kessel et al. Paper https://www.researchgate.net/publication/279269147

This residence index tool will take a compressed or uncompressed
detection file and caculate the residency index for each
station/receiver in the detections. A CSV file will be written to the
data directory for future use. A Pandas DataFrame is returned from the
function, which can be used to plot the information. The information
passed to the function is what is used to calculate the residence index,
**make sure you are only passing the data you want taken into
consideration for the residence index (i.e. species, stations, tags,
etc.)**.

**detections:** The CSV file in the data directory that is either
compressed or raw. If the file is not compressed please allow the
program time to compress the file and add the rows to the database. A
compressed file will be created in the data directory. Use the
compressed file for any future runs of the residence index function.

**calculation_method:** The method used to calculate the residence
index. Methods are:

-  kessel
-  timedelta
-  aggregate_with_overlap
-  aggregate_no_overlap.

**project_bounds:** North, South, East, and West bounding longitudes and
latitudes for visualization.

The calculation methods are listed and described below before they are
called. The function will default to the Kessel method when nothing is
passed.

Below is an example of inital variables to set up, which are the
detection file and the project bounds.

.. warning:: 

   Input files must include ``datecollected``, ``station``, ``longitude``, 
   ``latitude``, ``catalognumber``, and ``unqdetecid`` as columns.

.. code:: python

    from resonate import residence_index as ri
    import pandas as pd
    
    detections = pd.read_csv('/Path/to/detections.csv')

Kessel Residence Index Calculation
----------------------------------

The Kessel method converts both the startdate and enddate columns into a
date with no hours, minutes, or seconds. Next it creates a list of the
unique days where a detection was seen. The size of the list is returned
as the total number of days as an integer. This calculation is used to
determine the total number of distinct days (T) and the total number of
distinct days per station (S).

:math:`RI = \frac{S}{T}`

RI = Residence Index

S = Distinct number of days detected at the station

T = Distinct number of days detected anywhere on the array

.. warning:: 

   Possible rounding error may occur as a detection on ``2016-01-01 23:59:59``
   and a detection on ``2016-01-02 00:00:01`` would be counted as two days when it is really 2-3 seconds.

Kessel RI Example Code
~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    kessel_ri = ri.residency_index(detections, calculation_method='kessel')
    
    ri.plot_ri(kessel_ri)

Timedelta Residence Index Calculation
-------------------------------------

The Timedelta calculation method determines the first startdate of all
detections and the last enddate of all detections. The time difference
is then taken as the values to be used in calculating the residence
index. The timedelta for each station is divided by the timedelta of the
array to determine the residence index.

:math:`RI = \frac{\Delta S}{\Delta T}`

RI = Residence Index

:math:`\Delta S` = Last detection time at a station - First detection
time at the station

:math:`\Delta T` = Last detection time on an array - First detection
time on the array

Timedelta RI Example Code
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    timedelta_ri = ri.residency_index(detections, calculation_method='timedelta')
    
    ri.plot_ri(timedelta_ri)

Aggregate With Overlap Residence Index Calculation
--------------------------------------------------

The Aggregate With Overlap calculation method takes the length of time
of each detection and sums them together. A total is returned. The sum
for each station is then divided by the sum of the array to determine
the residence index.

RI = :math:`\frac{AwOS}{AwOT}` 

RI = Residence Index

AwOS = Sum of length of time of each detection at the station

AwOT = Sum of length of time of each detection on the array

Aggregate With Overlap RI Example Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    with_overlap_ri = ri.residency_index(detections, calculation_method='aggregate_with_overlap')
    
    ri.plot_ri(with_overlap_ri)

Aggregate No Overlap Residence Index Calculation
------------------------------------------------

The Aggregate No Overlap calculation method takes the length of time of
each detection and sums them together. However, any overlap in time
between one or more detections is excluded from the sum.

For example, if the first detection is from **2016-01-01 01:02:43** to
**2016-01-01 01:10:12** and the second detection is from **2016-01-01
01:09:01** to **2016-01-01 01:12:43**, then the sume of those two
detections would be 10 minutes.

A total is returned once all detections of been added without overlap.
The sum for each station is then divided by the sum of the array to
determine the residence index.

RI = :math:`\frac{AnOS}{AnOT}` 

RI = Residence Index

AnOS = Sum of length of time of each detection at the station, excluding
any overlap

AnOT = Sum of length of time of each detection on the array, excluding
any overlap

Aggregate No Overlap RI Example Code
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    no_overlap_ri = ri.residency_index(detections, calculation_method='aggregate_no_overlap')
    
    ri.plot_ri(no_overlap_ri, title="ANO RI")

Mapbox
------

Alternatively you can use a Mapbox access token plot your map. Mapbox is
much for responsive than standard Scattergeo plot.

Mapbox Example Code
~~~~~~~~~~~~~~~~~~~

.. code:: python

    mapbox_access_token = 'YOUR MAPBOX ACCESS TOKEN HERE'
    kessel_ri = ri.residency_index(detections, calculation_method='kessel')
    ri.plot_ri(kessel_ri, mapbox_token=mapbox_access_token,marker_size=40, scale_markers=True)

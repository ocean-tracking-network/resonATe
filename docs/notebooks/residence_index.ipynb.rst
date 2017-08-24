
Residence Index
===============

This residence index tool will take a compressed or uncompressed
detection file and caculate the residency index for each
station/receiver in the detections. A CSV file will be written to the
data directory for future use. A Pandas DataFrame is returned from the
function, which can be used to plot the information. The information
passed to the function is what is used to calculate the residence index,
**make sure you are only passing the data you want taken into
consideration for the residence index (i.e. species, stations, tags,
etc.)**.

**detections:** The CSV file in the data directory that is either
compressed or raw. If the file is not compressed please allow the
program time to compress the file and add the rows to the database. A
compressed file will be created in the data directory. Use the
compressed file for any future runs of the residence index function.

.. raw:: html

   <hr/>

**calculation\_method:** The method used to calculate the residence
index.

Methods are: - kessel - timedelta - aggregate\_with\_overlap -
aggregate\_no\_overlap.

The calculation methods are listed and described below before they are
called. The function will default to the Kessel method when nothing is
passed.

.. raw:: html

   <hr/>

**table:** The database table to use to determine the station/receiver
location(lat, long). If no table is passed the function will try to
determine the table name from detection file name.

.. raw:: html

   <hr/>

**Kessel et al. Paper -
https://www.researchgate.net/publication/279269147 **

.. code:: python

    from otntoolbox import kessel_ri as ri
    import matplotlib
    %matplotlib inline
    
    project_bounds = {'north': 44.54, 
                      'south': 42.84, 
                      'east': -61.93, 
                      'west': -64.18}
    
    # Declare the uncompressed detections file you want to plot
    detfile = "../tests/assertion_files/nsbs.csv"

Kessel Residence Index Calculation
----------------------------------

The Kessel method converts both the startdate and enddate columns into a
date with no hours, minutes, or seconds. Next it creates a list of the
unique days where a detection was seen. The size of the list is returned
as the total number of days as an integer. This calculation is used to
determine the total number of distinct days (T) and the total number of
distinct days per station (S).

.. raw:: html

   <hr/>

:math:`RI = \frac{S}{T}`

RI = Residence Index

S = Distinct number of days detected at the station

T = Distinct number of days detected anywhere on the array

.. raw:: html

   <hr/>

\*\*\* NOTE \*\*\*\* Possible rounding error may occur as a detection on
2016-01-01 23:59:59 and a detection on 2016-01-02 00:00:01 would be
counted as two days when it is really 2-3 seconds.

.. code:: python

    # From Raw Detection File
    kessel_ri = ri.residency_index(detfile, calculation_method='kessel')
    ri.plot_ri(kessel_ri, bounds=project_bounds)

Timedelta Residence Index Calculation
-------------------------------------

The Timedelta calculation method determines the first startdate of all
detections and the last enddate of all detections. The time difference
is then taken as the values to be used in calculating the residence
index. The timedelta for each station is divided by the timedelta of the
array to determine the residence index.

.. raw:: html

   <hr/>

:math:`RI = \frac{\Delta S}{\Delta T}`

RI = Residence Index

:math:`\Delta S` = Last detection time at a station - First detection
time at the station

:math:`\Delta T` = Last detection time on an array - First detection
time on the array

.. code:: python

    # From Raw Detection File
    timedelta_ri = ri.residency_index(detfile, calculation_method='timedelta')
    
    ri.plot_ri(timedelta_ri, bounds=project_bounds)

Aggregate With Overlap Residence Index Calculation
--------------------------------------------------

The Aggregate With Overlap calculation method takes the length of time
of each detection and sums them together. A total is returned. The sum
for each station is then divided by the sum of the array to determine
the residence index.

.. raw:: html

   <hr/>

RI = :math:`\frac{AwOS}{AwOT}` 

RI = Residence Index

AwOS = Sum of length of time of each detection at the station

AwOT = Sum of length of time of each detection on the array

.. code:: python

    # From Raw Detection File
    with_overlap_ri = ri.residency_index(detfile, calculation_method='aggregate_with_overlap')
    
    ri.plot_ri(with_overlap_ri, bounds=project_bounds)

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

.. raw:: html

   <hr/>

RI = :math:`\frac{AnOS}{AnOT}` 

RI = Residence Index

AnOS = Sum of length of time of each detection at the station, excluding
any overlap

AnOT = Sum of length of time of each detection on the array, excluding
any overlap

.. code:: python

    # From Raw Detection File
    no_overlap_ri = ri.residency_index(detfile, calculation_method='aggregate_no_overlap')
    
    ri.plot_ri(no_overlap_ri, project=project_bounds)

.. code:: python

    ri.interactive_map(kessel_ri)

Filtering Detections on Distance / Time
=======================================

White/Mihoff Filter
-------------------

*(White, E., Mihoff, M., Jones, B., Bajona, L., Halfyard, E. 2014.
White-Mihoff False Filtering Tool)*

OTN has developed a tool which will assist with filtering false
detections. The first level of filtering involves identifying isolated
detections. The original concept came from work done by Easton White. He
was kind enough to share his research database with OTN. We did some
preliminary research and developed a proposal for a filtering tool based
on what Easton had done. This proof of concept was presented to Steve
Kessel and Eddie Halfyard in December 2013 and a decision was made to
develop a tool for general use.

This is a very simple tool. It will take an input file of detections and
based on an input parameter will identify suspect detections. The
suspect detections will be put into a dataframe which the user can
examine. There will be enough information for each suspect detection for
the user to understand why it was flagged. There is also enough
information to be able to reference the detection in the original file
if the user wants to see what was happening at the same time.

The input parameter is a time in seconds. We used 3600 seconds as the
default as this is what was used in Easton’s code. This value can be
changed by the user. The output contains a record for each detection for
which there has been more than xx seconds since the previous detection
(of that tag/animal) and more than the same amount of time until the
next detection. It ignores which receiver the detection occurred at.
That is all it does, nothing more and nothing less.

Below the interval is set to 3600 seconds and is not using a a user
specified suspect file. The function will also create a distance matrix.

.. warning:: 

   Input files must include ``datecollected``, ``catalognumber``, ``station`` and ``unqdetecid`` as columns.

.. code:: python

    from resonate.filters import get_distance_matrix
    from resonate.filters import filter_detections
    import pandas as pd
    
    detections = pd.read_csv('/path/to/detections.csv')
    
    time_interval = 3600 # in seconds
    
    SuspectFile = None
    
    CreateDistanceMatrix = True
    
    filtered_detections = filter_detections(detections, 
                                            suspect_file=SuspectFile, 
                                            min_time_buffer=time_interval,
                                            distance_matrix=CreateDistanceMatrix)




    ---------------------------------------------------------------------------

    ModuleNotFoundError                       Traceback (most recent call last)

    Cell In[1], line 1
    ----> 1 from resonate.filters import get_distance_matrix
          2 from resonate.filters import filter_detections
          3 import pandas as pd


    ModuleNotFoundError: No module named 'resonate'


You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    filtered_detections['filtered'].to_csv('/path/to/output.csv', index=False)
    
    filtered_detections['suspect'].to_csv('/path/to/output.csv', index=False)
    
    filtered_detections['dist_mtrx'].to_csv('/path/to/output.csv', index=False)

Distance Filter
---------------

The distance filter will separate detections based only on distance. The
``maximum_distance`` argument defaults to 100,000 meters (or 100
kilometers), but can be adjusted. Any detection where the succeeding and
preceding detections are more than the ``maximum_distance`` away will be
considered suspect.

.. warning:: 

   Input files must include ``datecollected``, ``catalognumber``, ``station`` and ``unqdetecid`` as columns.

.. code:: python

    from resonate.filters import distance_filter
    import pandas as pd
    
    detections = pd.read_csv('/path/to/detections.csv')
    
    
    filtered_detections = distance_filter(detections)

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    filtered_detections['filtered'].to_csv('/path/to/output.csv', index=False)
    
    filtered_detections['suspect'].to_csv('/path/to/output.csv', index=False)

Velocity Filter
---------------

The velocity filter will separate detections based on the animal’s
velocity. The ``maximum_velocity`` argument defaults to 10 m/s, but can
be adjusted. Any detection where the succeeding and preceding velocities
of an animal are more than the ``maximum_velocity`` will be considered
suspect.

.. warning:: 

   Input files must include ``datecollected``, ``catalognumber``, ``station`` and ``unqdetecid`` as columns.

.. code:: python

    from resonate.filters import velocity_filter
    import pandas as pd
    
    detections = pd.read_csv('/path/to/detections.csv')
    
    
    filtered_detections = velocity_filter(detections)

You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    filtered_detections['filtered'].to_csv('/path/to/output.csv', index=False)
    
    filtered_detections['suspect'].to_csv('/path/to/output.csv', index=False)

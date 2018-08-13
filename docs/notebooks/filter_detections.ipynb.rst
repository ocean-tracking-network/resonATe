
Filtering Detections on Distance / Time
=======================================

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

The input parameter is a time in minutes. We used 60 minutes as the
default as this is what was used in Easton’s code. This value can be
changed by the user. The output contains a record for each detection for
which there has been more than xx minutes since the previous detection
(of that tag/animal) and more than the same amount of time until the
next detection. It ignores which receiver the detection occurred at.
That is all it does, nothing more and nothing less.

Below the interval is set to 60 minutes and is not using a a user
specified suspect file. The function will also create a distance matrix.

.. warning:: 

   Input files must include ``datecollected``, ``catalognumber``, ``station`` and ``unqdetecid`` as columns.

.. code:: python

    from resonate.filter_detections import get_distance_matrix
    from resonate.filter_detections import filter_detections
    import pandas as pd
    
    detections = pd.read_csv('/path/to/detections.csv')
    
    time_interval = 60 # in Minutes
    
    SuspectFile = None
    
    CreateDistanceMatrix = True
    
    filtered_detections = filter_detections(detections, 
                                            suspect_file=SuspectFile, 
                                            min_time_buffer=time_interval,
                                            distance_matrix=CreateDistanceMatrix)


You can use the Pandas ``DataFrame.to_csv()`` function to output the
file to a desired location.

.. code:: python

    filtered_detections['filtered'].to_csv('../tests/assertion_files/nsbs_filtered.csv', index=False)
    
    filtered_detections['suspect'].to_csv('/path/to/output.csv', index=False)
    
    filtered_detections['dist_mtrx'].to_csv('/path/to/output.csv', index=False)

.. code:: python

    from resonate.filter_detections import distance_filter
    import pandas as pd
    
    detections = pd.read_csv('../tests/assertion_files/nsbs.csv')
    
    
    filtered_detections = distance_filter(detections)

.. code:: python

    filtered_detections['filtered'].to_csv('../tests/assertion_files/nsbs_distance_filtered.csv', index=False)

.. code:: python

    from resonate.filter_detections import velocity_filter
    import pandas as pd
    
    detections = pd.read_csv('../tests/assertion_files/nsbs.csv')
    
    
    filtered_detections = velocity_filter(detections)

.. code:: python

    filtered_detections['filtered'].to_csv('../tests/assertion_files/nsbs_velocity_filtered.csv', index=False)

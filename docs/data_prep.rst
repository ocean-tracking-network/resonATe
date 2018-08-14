Preparing Data
==============

resonATe requires your acoustic telemetry data to have specific column headers. The column headers are the same ones used by the Ocean Tracking Network for their detection extracts.

The columns you need are as follows:

- **catalognumber** - A unique identifier assigned to an animal.
- **station**  - A unique identifier for the station or mooring where the receiver was located. This column is used in resonATe for grouping detections which should be considered to have occurred in the same place.
- **datecollected** - Date and time of release or detection, all of which have the same timezone (example format: ``2018-02-02 04:09:45``).
- **longitude** - The receiver location at time of detection in decimal degrees.
- **latitude** -  The receiver location at time of detection in decimal degrees.
- **scientificname** - The taxonmoic name for the animal detected.
- **fieldnumber** - The unique number for the tag/device attached to the animal.
- **unqdetecid** - A unique value assigned to each record in the data. resonATe includes a function to generate this column if needed. Details in :ref:`Unique Detections ID <unq_detections_id_page>`.

The :ref:`Receiver Efficiency Index <receiver_efficiency_index_page>` also needs a deployment history for stations. The columns for deployments are as follows:

- **station_name** - A unique identifier for the station or mooring where the receiver was located. This column is used in resonATe for grouping detections which should be considered to have occurred in the same place.
- **deploy_date** - A date of when the receiver was placed in a water or is active (example format: ``2018-02-02``).
- **recovery_date** - A date of when the receiver was removed from the water or became inactive (example format: ``2018-02-02``).
- **last_download** - A date of the last time data was retrieved from the receiver (example format: ``2018-02-02``).

All other columns are not required and will not affect the functions; however, they may be used in some functions. For example, ``receiver_group`` can be used color code data in the :ref:`Abacus Plot <abacus_plot_page>`.

.. warning::

    Detection records from mobile receivers, i.e. from receivers attached to gliders or animals, as well as satellite transmitter detections, will not necessarily be appropriate or compatible for use with all of these tools.

Renaming Columns
----------------

`Pandas`_  provides a ``rename()`` function that can be implemented as follows:

.. _Pandas: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.rename.html

.. code:: python

    import pandas as pd

    df = pd.read_csv('/path/to/detections.csv')

    df.rename(index=str, columns={
      'your_animal_id_column':'catalognumber',
      'your_station_column':'station',
      'your_date_time_column':'datecollected',
      'your_longitude_column':'longitude',
      'your_latitude_column':'latitude',
      'your_unique_id_column':'unqdetecid'
    }, inplace=True)

Example Dataset
---------------

.. csv-table::
   :header: catalognumber,scientificname,commonname,receiver_group,station,datecollected,timezone,longitude,latitude,unqdetecid
   :file: _static/nsbs.csv

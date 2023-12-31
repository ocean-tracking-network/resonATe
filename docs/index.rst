.. resonate documentation master file, created by
   sphinx-quickstart on Mon Apr 16 21:22:43 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

resonATe Overview
====================

resonATe is the Ocean Tracking Network's acoustic telemetry analysis toolkit.
It can be used to filter, compress, visualize and analyze acoustic detection
extracts from OTN and other marine telemetry data.

* :ref:`Abacus Plot <abacus>`
* :ref:`Bubble Plot <bubble>`
* :ref:`Cohort <cohort>`
* :ref:`Compressing Detections  <compress>`
* :ref:`Distance Matrix  <distance_matrix>`
* :ref:`Filtering  <filter>`
* :ref:`Interval Data <interval>`
* :ref:`Residence Index <residence_index>`
* :ref:`Receiver Efficiency Index <receiver_efficiency>`
* :ref:`Unique ID  <unqid>`
* :ref:`Visual Timeline <timeline>`


.. _abacus:

Abacus Plot
-----------

The abacus plot is a way to plot annimal along time. The function uses Plotly to place your points on a scatter plot. ``ycolumn`` is used as the y axis and ``datecollected`` is used as the x axis. ``color_column`` is used to group detections together and assign them a color. Details are in :ref:`Abacus Plot <abacus_plot_page>`.

.. _bubble:

Bubble Plot
-----------

The bubble plot function returns a Plotly scatter plot layered ontop of a map. The color of the markers will indicate the number of detections at each location. Alternatively, you can indicate the number of individuals seen at each location by using ``type = 'individual'``. Details are in :ref:`Bubble Plot <bubble_plot_page>`.

.. _cohort:

Cohort
------

The tool takes a file of compressed detections and a time parameter in minutes. It identifies groups of animals traveling together. Each station an animal visits is checked for other animals detected there within the specified time period. Details are in :ref:`Cohort Tool <cohort_page>`.

.. _compress:

Compressing Detections
----------------------

Compressing detections is done by looking at the detection times and locations of an animal. Any detections that occur successively in time, in the same location, and the time between detections does not exceed the ``timefilter``, are combined into a single detection with a start and end time. The result is a compressed detections Pandas DataFrame.

Compression is the first step of the Mihoff Interval Data Tool. Compressed detection DataFrames are needed for the tools, such as interval and cohort.  Details are in :ref:`Compression Tool <compression_page>`.


.. _filter:

Filtering
---------

*(White, E., Mihoff, M., Jones, B., Bajona, L., Halfyard, E. 2014. White-Mihoff False Filtering Tool)*


OTN has developed a tool which will assist with filtering false detections. The first level of filtering involves identifying isolated detections. The original concept came from work done by Easton White. He was kind enough to share his research database with OTN. We did some preliminary research and developed a proposal for a filtering tool based on what Easton had done. This proof of concept was presented to Steve Kessel and Eddie Halfyard in December 2013 and a decision was made to develop a tool for general use.

This is a very simple tool. It will take an input file of detections and based on an input parameter will identify suspect detections. The suspect detections will be put into a dataframe which the user can examine. There will be enough information for each suspect detection for the user to understand why it was flagged. There is also enough information to be able to reference the detection in the original file if the user wants to see what was happening at the same time.

The input parameter is a time in minutes. We used 3600 seconds as the default as this is what was used in Easton's code. This value can be changed by the user. The output contains a record for each detection for which there has been more than xx minutes since the previous detection (of that tag/animal) and more than the same amount of time until the next detection. It ignores which receiver the detection occurred at. That is all it does, nothing more and nothing less. Details are in :ref:`Filter Tool <filter_page>`.

Two other filtering tools are available as well, one based on distance alone and one based on velocity. They can be found at :ref:`Filter Tools <filter_page>` as well.


.. _distance_matrix:

Distance Matrix
---------------

This takes a DataFrame created by the White-Mihoff False Filtering tool. The file contains rows of station pairs with the straight line distance between them calculated in metres. A station pair will only be in the file if an animal traveled between the stations. If an animal goes from stn1 to stn2 and then to stn3, pairs stn1-stn2 and stn2-stn3 will be in the file. If no animal goes between stn1 and stn3, that pair will not be in the file. The tool also takes a file that the researcher provides of ‘real distances’.  The output will be a file which looks like the first file with the ‘real distance’ column updated. Details are in :ref:`Distance Matrix Tool <distance_matrix_page>`

.. _interval:

Interval Data
--------------------

*(Mihoff, M., Jones, B., Bajona, L., Halfyard, E. 2014. Mihoff Interval Data Tool)*

This tool will take a DataFrame of compressed detections and a distance matrix and output an interval DataFrame. The Interval DataFrame will contain records of the animal id, the arrival time at stn1, the departure time at stn1, the detection count at stn1, the arrival time at stn2, time between detections at the two stations, the interval in seconds, the distance between stations, and the velocity of the animal in m/s. Details are in :ref:`Interval Data Tool <interval_data_tool_page>`.


.. _residence_index:

Residence Index
---------------

This residence index tool will take a compressed or uncompressed detection file and caculate the residency index for each station/receiver in the detections. A CSV file will be written to the data directory for future use. A Pandas DataFrame is returned from the function, which can be used to plot the information. The information passed to the function is what is used to calculate the residence index, make sure you are only passing the data you want taken into consideration for the residence index (i.e. species, stations, tags, etc.). Details in :ref:`Residence Index Tool <residence_index_page>`.


.. _receiver_efficiency:

Receiver Efficiency Index
-------------------------

`(Ellis, R., Flaherty-Walia, K., Collins, A., Bickford, J., Walters Burnsed,  Lowerre-Barbieri S. 2018. Acoustic telemetry array evolution: from species- and project-specific designs to large-scale, multispecies, cooperative networks) <https://doi.org/10.1016/j.fishres.2018.09.015>`_

The receiver efficiency index is number between ``0`` and ``1`` indicating the amount of relative activity at each receiver compared to the entire set of receivers, regardless of positioning. The function takes a set detections and a deployment history of the receivers to create a context for the detections. Both the amount of unique tags and number of species are taken into consideration in the calculation. For the exact method, see the details in :ref:`Receiver Efficiency Index<receiver_efficiency_index_page>`.


.. _unqid:

Unique Id
---------

This tool will add a column to any file. The unique id will be sequential integers. No validation is done on the input file. Details in :ref:`Unique Detections ID <unq_detections_id_page>`.

.. _timeline:

Visual Timeline
---------------

This tool takes a detections extract file and generates a Plotly animated timeline, either in place in an iPython notebook or exported out to an HTML file. Details in :ref:`Visual Timeline <visual_timeline_page>`.

Contents:
---------

.. toctree::
   :maxdepth: 2

   self
   installation
   data_prep
   abacus_plot
   bubble_plot
   cohort
   compression
   filter
   interval_data
   residence_index
   receiver_efficiency_index
   notebooks/data_subsetting.ipynb
   unqid
   visual_timeline

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Receiver Efficiency Index
=========================

The receiver efficiency index is number between ``0`` and ``1``
indicating the amount of relative activity at each receiver compared to
the entire set of receivers, regardless of positioning. The function
takes a set detections and a deployment history of the receivers to
create a context for the detections. Both the amount of unique tags and
number of species are taken into consideration in the calculation.

The receiver efficiency index implement is implemented based on the
paper [paper place holder]. Each receiver’s index is calculated on the
formula of:

.. container:: large-math

   REI =
   :math:`\frac{T_r}{T_a} \times \frac{S_r}{S_a} \times \frac{DD_r}{DD_a} \times \frac{D_a}{D_r}`

.. raw:: html

   <hr/>

-  REI = Receiver Efficiency Index
-  :math:`T_r` = The number of tags detected on the receievr
-  :math:`T_a` = The number of tags detected across all receivers
-  :math:`S_r` = The number of species detected on the receiver
-  :math:`S_a` = The number of species detected across all receivers
-  :math:`DD_a` = The number of unique days with detections across all
   receivers
-  :math:`DD_r` = The number of unique days with detections on the
   receiver
-  :math:`D_a` = The number of days the array was active
-  :math:`D_r` = The number of days the receiver was active

Each REI is then normalized against the sum of all considered stations.
The result is a number between ``0`` and ``1`` indicating the relative
amount of activity at each receiver.

.. warning:: 

   Detection input files must include ``datecollected``, ``fieldnumber``, ``station``, and ``scientificname`` as columns and deployment input files must include ``station_name``, ``deploy_date``, ``last_download``, and ``recovery_date`` as columns.

``REI()`` takes two arguments. The first is a dataframe of detections
the detection timstamp, the station identifier, the species, and the tag
identifier. The next is a dataframe of deployments for each station. The
station name should match the stations in the detections. The
deployments need to include a deployment date and recovery date or last
download date. Details on the columns metnioned see the preparing data
section.

.. warning:: 

   This function assumes that no deployments for single station overlap. If deployments do overlap, the overlapping days will be counted twice.

.. code:: python

    from resonate.receiver_efficiency import REI
    
    detections = pd.read_csv('/path/to/detections.csv')
    deployments = pd.read_csv('/path/to/deployments.csv')
    
    station_REIs = REI(detections = detections, deployments = deployments)

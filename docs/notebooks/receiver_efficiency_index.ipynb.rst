
Receiver Efficiency Index
=========================

.. warning:: 

   Detection input files must include ``datecollected``, ``fieldnumber``, ``station``, and ``scientificname`` as columns and deployment input files must include ``station_name``, ``deploy_date``, ``last_download``, and ``recovery_date`` as columns.

.. code:: python

    from resonate.receiver_efficiency import REI
    
    detections = pd.read_csv('/path/to/detections.csv')
    deployments =. pd.read_csv('/path/to/deployments.csv')
    
    station_REIs = REI(detections = detections, deployments = deployments)

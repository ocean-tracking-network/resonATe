# -*- coding: utf-8 -*-
from resonate.filter_detections import get_distance_matrix
from resonate.compress import compress_detections
from resonate.interval_data_tool import interval_data
import pandas as pd
import geopy
import unittest
import pandas.testing as pt
from colorama import Fore as c



class IntervalTest(unittest.TestCase):

    def test_filter(self):
        print( c.YELLOW+'Testing Interval...'+c.RESET)
        input_file = pd.read_csv('tests/assertion_files/nsbs.csv')
        compressed = compress_detections(input_file) # compressed detections
        matrix = get_distance_matrix(input_file) # station distance matrix

        detection_radius = 400 # (in meters) applies same detection radius to all stations
        station_det_radius = pd.DataFrame([(x, geopy.distance.Distance(detection_radius/1000.0)) for x in matrix.columns.tolist()], columns=['station','radius'])
        station_det_radius.set_index('station', inplace=True)
        station_det_radius # preview radius values
        dfa = interval_data(compressed_df=compressed, dist_matrix_df=matrix, station_radius_df=station_det_radius)


        dfb = pd.read_csv('tests/assertion_files/nsbs_interval.csv')

        dfa = dfa.where((pd.notnull(dfa)), None)
        dfb = dfb.where((pd.notnull(dfb)), None)

        dfb.from_arrive = pd.to_datetime(dfb.from_arrive)
        dfb.from_leave = pd.to_datetime(dfb.from_leave)
        dfb.to_arrive = pd.to_datetime(dfb.to_arrive)
        dfb.to_leave = pd.to_datetime(dfb.to_leave)


        dfa.intervaltime = pd.to_timedelta(dfa.intervaltime)
        dfb.intervaltime = pd.to_timedelta(dfb.intervaltime)

        pt.assert_frame_equal(dfa, dfb)
        print( c.GREEN+'OK!\n'+c.RESET)


if __name__ == '__main__':
    unittest.main()

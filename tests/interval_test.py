# -*- coding: utf-8 -*-
from otntoolbox.filter_detections import get_distance_matrix
from otntoolbox.compress import compress_detections
from otntoolbox.interval_data_tool import interval_data
import pandas as pd
import geopy
import unittest
import pandas.testing as pt


class IntervalTest(unittest.TestCase):

    def test_filter(self):
        input_file = pd.read_csv('tests/assertion_files/nsbs.csv')
        compressed = compress_detections(input_file) # compressed detections
        matrix = get_distance_matrix(input_file) # station distance matrix

        detection_radius = 100 # (in meters) applies same detection radius to all stations
        station_det_radius = pd.DataFrame([(x, geopy.distance.Distance(detection_radius/1000.0)) for x in matrix.columns.tolist()], columns=['station','radius'])
        station_det_radius.set_index('station', inplace=True)
        station_det_radius # preview radius values
        dfa = interval_data(compressed_df=compressed, dist_matrix_df=matrix, station_radius_df=station_det_radius)
        dfa.drop(['to_leave', 'to_detcnt'], axis=1, inplace=True)
        dfb = pd.read_csv('tests/assertion_files/nsbs_interval.csv')
        dfb.from_arrive = pd.to_datetime(dfb.from_arrive)
        dfb.from_leave = pd.to_datetime(dfb.from_leave)
        dfb.to_arrive = pd.to_datetime(dfb.to_arrive)
        pt.assert_frame_equal(dfa, dfb)


if __name__ == '__main__':
    unittest.main()

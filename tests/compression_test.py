# -*- coding: utf-8 -*-
from otntoolbox.compress import compress_detections
import unittest
import pandas as pd
import pandas.testing as pt


class CompressionTest(unittest.TestCase):

    def test_compression(self):
        dfa = compress_detections(pd.read_csv('tests/assertion_files/nsbs.csv'))
        dfb = pd.read_csv('tests/assertion_files/nsbs_compressed.csv')
        dfb.startdate = pd.to_datetime(dfb.startdate)
        dfb.enddate = pd.to_datetime(dfb.enddate)
        dfb.avg_time_between_det = pd.to_timedelta(dfb.avg_time_between_det)
        pt.assert_frame_equal(dfa, dfb)


if __name__ == '__main__':
    unittest.main()

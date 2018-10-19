# -*- coding: utf-8 -*-
import unittest

import pandas as pd
import pandas.testing as pt
from colorama import Fore as c
from resonate.compress import compress_detections


class CompressionTest(unittest.TestCase):

    def test_compression(self):
        print(c.YELLOW + 'Testing Compression...' + c.RESET)
        dfa = compress_detections(pd.read_csv(
            'tests/assertion_files/nsbs.csv'))
        dfb = pd.read_csv('tests/assertion_files/nsbs_compressed.csv')
        dfb.startdate = pd.to_datetime(dfb.startdate)
        dfb.enddate = pd.to_datetime(dfb.enddate)
        dfb.avg_time_between_det = pd.to_timedelta(dfb.avg_time_between_det)
        pt.assert_frame_equal(dfa, dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)


if __name__ == '__main__':
    unittest.main()

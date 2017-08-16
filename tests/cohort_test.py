# -*- coding: utf-8 -*-
from otntoolbox.cohorts import cohort
from otntoolbox.compress import compress_detections
import unittest
import pandas as pd
import pandas.testing as pt


class CohortTest(unittest.TestCase):

    def test_cohort(self):
        compressed = compress_detections(pd.read_csv('tests/assertion_files/nsbs_no_releases.csv'))
        dfa = cohort(compressed, 60)
        dfb = pd.read_csv('tests/assertion_files/nsbs_cohort_60min.csv')
        pt.assert_frame_equal(dfa, dfb)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
import otntoolbox.kessel_ri as ri
import unittest
import pandas as pd
import pandas.testing as pt


class ResidenceIndexTest(unittest.TestCase):

    def test_kessel(self):
        dfa = ri.residency_index('tests/assertion_files/nsbs_matched_detections_2014.csv', calculation_method='kessel')
        dfb = pd.read_csv('tests/assertion_files/nsbs_kessel_ri.csv')
        pt.assert_frame_equal(dfa, dfb)

    def test_timedelta(self):
        dfa = ri.residency_index('tests/assertion_files/nsbs_matched_detections_2014.csv', calculation_method='timedelta')
        dfb = pd.read_csv('tests/assertion_files/nsbs_timedelta_ri.csv')
        pt.assert_frame_equal(dfa, dfb)

    def test_aggregate_with_overlap(self):
        dfa = ri.residency_index('tests/assertion_files/nsbs_matched_detections_2014.csv', calculation_method='aggregate_with_overlap')
        dfb = pd.read_csv('tests/assertion_files/nsbs_aggregate_with_overlap_ri.csv')
        pt.assert_frame_equal(dfa, dfb)

    def test_aggregate_no_overlap(self):
        dfa = ri.residency_index('tests/assertion_files/nsbs_matched_detections_2014.csv', calculation_method='aggregate_no_overlap')
        dfb = pd.read_csv('tests/assertion_files/nsbs_aggregate_no_overlap_ri.csv')
        pt.assert_frame_equal(dfa, dfb)

if __name__ == '__main__':
    unittest.main()

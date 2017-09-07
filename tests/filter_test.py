# -*- coding: utf-8 -*-
from otntoolbox.filter_detections import filter_detections
import unittest
import pandas as pd
import pandas.testing as pt


class FilterTest(unittest.TestCase):

    def test_filter(self):
        dfa = filter_detections('tests/assertion_files/nsbs.csv')['filtered']
        dfb = pd.read_csv('tests/assertion_files/nsbs_filtered.csv')
        dfa.notes = dfa.notes.astype(float)
        dfb.datecollected = pd.to_datetime(dfb.datecollected)
        pt.assert_frame_equal(dfa.reset_index(drop=True), dfb)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
import unittest

import pandas as pd
import pandas.testing as pt
from colorama import Fore as c
from resonate.determine_format import detect

from resonate.filters import (distance_filter, filter_detections,
                              velocity_filter, filter_all)


class FilterTest(unittest.TestCase):

    def test_filter(self):
        print(c.YELLOW + 'Testing Filtering...' + c.RESET)
        input_file = pd.read_csv('tests/assertion_files/nsbs.csv')
        dfa = filter_detections(input_file, add_column=False, **detect(input_file))['filtered']
        dfb = pd.read_csv('tests/assertion_files/nsbs_filtered.csv')
        dfa.notes = dfa.notes.astype(float)
        dfa.datecollected = pd.to_datetime(dfa.datecollected)
        dfb.datecollected = pd.to_datetime(dfb.datecollected)
        pt.assert_frame_equal(dfa.reset_index(drop=True), dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)

    def test_distance_filter(self):
        print(c.YELLOW + 'Testing Distance Filtering...' + c.RESET)
        input_file = pd.read_csv('tests/assertion_files/nsbs.csv')
        dfa = distance_filter(input_file, add_column=False, **detect(input_file))['filtered']
        dfb = pd.read_csv(
            'tests/assertion_files/nsbs_distance_filtered.csv')
        pt.assert_frame_equal(dfa.reset_index(drop=True), dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)

    def test_velocity_filter(self):
        print(c.YELLOW + 'Testing Velocity Filtering...' + c.RESET)
        input_file = pd.read_csv('tests/assertion_files/nsbs.csv')
        dfa = velocity_filter(input_file, add_column=False, **detect(input_file))['filtered']
        dfb = pd.read_csv(
            'tests/assertion_files/nsbs_velocity_filtered.csv')
        dfb.datecollected = pd.to_datetime(dfb.datecollected)
        dfb.lag_time_diff = pd.to_timedelta(dfb.lag_time_diff)
        dfb.lead_time_diff = pd.to_timedelta(dfb.lead_time_diff)
        pt.assert_frame_equal(dfa.reset_index(drop=True), dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)
    
    def test_filter_all(self):
        print(c.YELLOW + 'Testing Filtering All...' + c.RESET)
        input_file = pd.read_csv('tests/assertion_files/nsbs.csv')
        dfa = filter_all(input_file, **detect(input_file))
        dfb = pd.read_csv(
            'tests/assertion_files/nsbs_filter_all.csv', low_memory=False)
        dfa.passed_detection_filter = dfa.passed_detection_filter.astype(bool)
        dfb.datecollected = pd.to_datetime(dfb.datecollected)
        dfb.lag_time_diff = pd.to_timedelta(dfb.lag_time_diff)
        dfb.lead_time_diff = pd.to_timedelta(dfb.lead_time_diff)
        pt.assert_frame_equal(dfa.reset_index(drop=True), dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)


if __name__ == '__main__':
    unittest.main()

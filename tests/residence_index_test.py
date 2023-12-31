# -*- coding: utf-8 -*-
import unittest

import pandas as pd
import pandas.testing as pt
import resonate.residence_index as ri
from colorama import Fore as c


class ResidenceIndexTest(unittest.TestCase):

    def test_kessel(self):
        print(c.YELLOW + 'Testing Kessel RI...' + c.RESET)
        dfa = ri.residency_index(pd.read_csv(
            'tests/assertion_files/nsbs.csv'), calculation_method='kessel')
        dfb = pd.read_csv('tests/assertion_files/nsbs_kessel_ri.csv')
        dfa.sort_values(['station', 'days_detected'], inplace=True)
        dfb.sort_values(['station', 'days_detected'], inplace=True)
        dfa.reset_index(inplace=True, drop=True)
        dfb.reset_index(inplace=True, drop=True)
        pt.assert_frame_equal(dfa, dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)

    def test_timedelta(self):
        print(c.YELLOW + 'Testing Timedelta RI...' + c.RESET)
        dfa = ri.residency_index(pd.read_csv(
            'tests/assertion_files/nsbs.csv'), calculation_method='timedelta')
        dfb = pd.read_csv('tests/assertion_files/nsbs_timedelta_ri.csv')
        dfa.sort_values(['station', 'days_detected'], inplace=True)
        dfb.sort_values(['station', 'days_detected'], inplace=True)
        dfa.reset_index(inplace=True, drop=True)
        dfb.reset_index(inplace=True, drop=True)
        pt.assert_frame_equal(dfa, dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)

    def test_aggregate_with_overlap(self):
        print(c.YELLOW + 'Testing Aggregate With Overlap RI...' + c.RESET)
        dfa = ri.residency_index(pd.read_csv(
            'tests/assertion_files/nsbs.csv'), calculation_method='aggregate_with_overlap')
        dfb = pd.read_csv(
            'tests/assertion_files/nsbs_aggregate_with_overlap_ri.csv')
        dfa.sort_values(['station', 'days_detected'], inplace=True)
        dfb.sort_values(['station', 'days_detected'], inplace=True)
        dfa.reset_index(inplace=True, drop=True)
        dfb.reset_index(inplace=True, drop=True)
        pt.assert_frame_equal(dfa, dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)

    def test_aggregate_no_overlap(self):
        print(c.YELLOW + 'Testing Aggregate No Overlap RI...' + c.RESET)
        dfa = ri.residency_index(pd.read_csv(
            'tests/assertion_files/nsbs.csv'), calculation_method='aggregate_no_overlap')
        dfb = pd.read_csv(
            'tests/assertion_files/nsbs_aggregate_no_overlap_ri.csv')
        dfa.sort_values(['station', 'days_detected'], inplace=True)
        dfb.sort_values(['station', 'days_detected'], inplace=True)
        dfa.reset_index(inplace=True, drop=True)
        dfb.reset_index(inplace=True, drop=True)
        pt.assert_frame_equal(dfa, dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)


if __name__ == '__main__':
    unittest.main()

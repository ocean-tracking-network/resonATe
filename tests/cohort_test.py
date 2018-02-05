# -*- coding: utf-8 -*-
from resonate.cohorts import cohort
from resonate.compress import compress_detections
import unittest
import pandas as pd
import pandas.testing as pt
from colorama import Fore as c


class CohortTest(unittest.TestCase):

    def test_cohort(self):
        print(c.YELLOW+'Testing Cohort...'+c.RESET)
        compressed = compress_detections(pd.read_csv('tests/assertion_files/nsbs.csv'))
        dfa = cohort(compressed, 60)
        dfb = pd.read_csv('tests/assertion_files/nsbs_cohort_60min.csv')
        dfb.anml_2_arrive = pd.to_datetime(dfb.anml_2_arrive)
        dfb.anml_2_depart = pd.to_datetime(dfb.anml_2_depart)
        pt.assert_frame_equal(dfa, dfb)
        print(c.GREEN+'OK!\n'+c.RESET)


if __name__ == '__main__':
    unittest.main()

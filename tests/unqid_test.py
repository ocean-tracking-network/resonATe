# -*- coding: utf-8 -*-
from otntoolbox.uniqueid import add_unqdetecid
import unittest
import pandas as pd
import pandas.testing as pt


class UniqueDetectionIdTest(unittest.TestCase):

    def test_add_unqdetecid(self):
        dfa = add_unqdetecid('tests/assertion_files/nsbs_nounq.csv')
        dfb = pd.read_csv('tests/assertion_files/nsbs_unqid.csv')
        pt.assert_frame_equal(dfa, dfb)

if __name__ == '__main__':
    unittest.main()
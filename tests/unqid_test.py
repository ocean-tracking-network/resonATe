# -*- coding: utf-8 -*-
from resonate.uniqueid import add_unqdetecid
import unittest
import pandas as pd
import pandas.testing as pt
from colorama import Fore as c


class UniqueDetectionIdTest(unittest.TestCase):

    def test_add_unqdetecid(self):
        print( c.YELLOW+'Testing Unique ID...'+c.RESET)
        dfa = add_unqdetecid('tests/assertion_files/nsbs_nounq.csv')
        dfb = pd.read_csv('tests/assertion_files/nsbs_unqid.csv')
        pt.assert_frame_equal(dfa, dfb)
        print( c.GREEN+'OK!\n'+c.RESET)


if __name__ == '__main__':
    unittest.main()

# -*- coding: utf-8 -*-
import unittest

import pandas as pd
import pandas.testing as pt
from colorama import Fore as c
from resonate.receiver_efficiency import REI


class REITest(unittest.TestCase):

    def test_compression(self):
        print(c.YELLOW + 'Testing REI...' + c.RESET)

        detections = pd.read_csv('tests/assertion_files/hfx_detections.csv')
        deployments = pd.read_csv('tests/assertion_files/hfx_deployments.csv')

        dfa = REI(detections, deployments)
        dfb = pd.read_csv('tests/assertion_files/hfx_rei.csv')
        pt.assert_frame_equal(dfa, dfb)
        print(c.GREEN + 'OK!\n' + c.RESET)


if __name__ == '__main__':
    unittest.main()

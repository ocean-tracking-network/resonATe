# -*- coding: utf-8 -*-
import unittest

import pandas as pd
import pandas.testing as pt
from colorama import Fore as c
import pickle
import pytest
from resonate.att_formatter import create_att_dictionary_format
from resonate.determine_format import detect

class ATTFormatterTest(unittest.TestCase):
    @pytest.mark.filterwarnings("ignore:Workbook contains no default style, apply openpyxl's default")
    def test_att_formatter(self):
        print(c.YELLOW + 'Testing ATT Formatter...' + c.RESET)
        dets = "tests/assertion_files/nsbs_2014_short.csv"
        tags = "tests/assertion_files/nsbs_tag_metadata.xls"
        deployments = "tests/assertion_files/hfx_deployments.xlsx"

        att = create_att_dictionary_format(dets,
                                     tags,
                                     deployments,
                                     **detect(dets))
        with open("tests/assertion_files/att_archive.pkl", 'rb') as f:
            att_archive = pickle.load(f)
        pt.assert_frame_equal(att['tag_detections'], att_archive['tag_detections'])
        pt.assert_frame_equal(att['tag_metadata'], att_archive['tag_metadata'])
        pt.assert_frame_equal(att['station_information'], att_archive['station_information'])
        print(c.GREEN + 'OK!\n' + c.RESET)

if __name__ == '__main__':
    unittest.main()

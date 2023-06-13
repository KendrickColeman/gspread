import unittest

import gspread
import gspread.utils as utils


class UtilsTest(unittest.TestCase):
    def test_extract_id_from_url(self):
        url_id_list = [
            # New-style url
            (
                "https://docs.google.com/spreadsheets/d/"
                "1qpyC0X3A0MwQoFDE8p-Bll4hps/edit#gid=0",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            (
                "https://docs.google.com/spreadsheets/d/"
                "1qpyC0X3A0MwQoFDE8p-Bll4hps/edit",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            (
                "https://docs.google.com/spreadsheets/d/" "1qpyC0X3A0MwQoFDE8p-Bll4hps",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
            # Old-style url
            (
                "https://docs.google.com/spreadsheet/"
                "ccc?key=1qpyC0X3A0MwQoFDE8p-Bll4hps&usp=drive_web#gid=0",
                "1qpyC0X3A0MwQoFDE8p-Bll4hps",
            ),
        ]

        for url, id in url_id_list:
            self.assertEqual(id, utils.extract_id_from_url(url))

    def test_no_extract_id_from_url(self):
        self.assertRaises(
            gspread.NoValidUrlKeyFound, utils.extract_id_from_url, "http://example.org"
        )

    def test_a1_to_rowcol(self):
        self.assertEqual(utils.a1_to_rowcol("ABC3"), (3, 731))

    def test_rowcol_to_a1(self):
        self.assertEqual(utils.rowcol_to_a1(3, 731), "ABC3")
        self.assertEqual(utils.rowcol_to_a1(1, 104), "CZ1")

    def test_addr_converters(self):
        for row in range(1, 257):
            for col in range(1, 512):
                addr = utils.rowcol_to_a1(row, col)
                (r, c) = utils.a1_to_rowcol(addr)
                self.assertEqual((row, col), (r, c))

    def test_get_gid(self):
        gid = "od6"
        self.assertEqual(utils.wid_to_gid(gid), "0")
        gid = "osyqnsz"
        self.assertEqual(utils.wid_to_gid(gid), "1751403737")
        gid = "ogsrar0"
        self.assertEqual(utils.wid_to_gid(gid), "1015761654")

    def test_numericise(self):
        self.assertEqual(utils.numericise("faa"), "faa")
        self.assertEqual(utils.numericise("3"), 3)
        self.assertEqual(utils.numericise("3_2"), "3_2")
        self.assertEqual(
            utils.numericise("3_2", allow_underscores_in_numeric_literals=False), "3_2"
        )
        self.assertEqual(
            utils.numericise("3_2", allow_underscores_in_numeric_literals=True), 32
        )
        self.assertEqual(utils.numericise("3.1"), 3.1)
        self.assertEqual(utils.numericise("", empty2zero=True), 0)
        self.assertEqual(utils.numericise("", empty2zero=False), "")
        self.assertEqual(utils.numericise("", default_blank=None), None)
        self.assertEqual(utils.numericise("", default_blank="foo"), "foo")
        self.assertEqual(utils.numericise(""), "")
        self.assertEqual(utils.numericise(None), None)

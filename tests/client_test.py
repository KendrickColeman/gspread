# -*- coding: utf-8 -*-

import gspread
import gspread.utils as utils
from gspread.exceptions import APIError

from .test import GspreadTest


class ClientTest(GspreadTest):

    """Test for gspread.client."""

    def test_no_found_exeption(self):
        noexistent_title = "Please don't use this phrase as a name of a sheet."
        self.assertRaises(gspread.SpreadsheetNotFound, self.gc.open, noexistent_title)

    def test_openall(self):
        spreadsheet_list = self.gc.openall()
        spreadsheet_list2 = self.gc.openall(spreadsheet_list[0].title)

        self.assertTrue(len(spreadsheet_list2) < len(spreadsheet_list))
        for s in spreadsheet_list:
            self.assertTrue(isinstance(s, gspread.Spreadsheet))
        for s in spreadsheet_list2:
            self.assertTrue(isinstance(s, gspread.Spreadsheet))

    def test_create(self):
        title = "Test Spreadsheet"
        new_spreadsheet = self.gc.create(title)
        self.assertTrue(isinstance(new_spreadsheet, gspread.Spreadsheet))

    def test_copy(self):
        original_spreadsheet = self.gc.create("Original")
        spreadsheet_copy = self.gc.copy(original_spreadsheet.id)
        self.assertTrue(isinstance(spreadsheet_copy, gspread.Spreadsheet))

        original_metadata = original_spreadsheet.fetch_sheet_metadata()
        copy_metadata = spreadsheet_copy.fetch_sheet_metadata()
        self.assertEqual(original_metadata["sheets"], copy_metadata["sheets"])

    def test_import_csv(self):
        title = "TestImportSpreadsheet"
        new_spreadsheet = self.gc.create(title)

        sg = self._sequence_generator()

        csv_rows = 4
        csv_cols = 4

        rows = [[next(sg) for j in range(csv_cols)] for i in range(csv_rows)]

        simple_csv_data = "\n".join([",".join(row) for row in rows])

        self.gc.import_csv(new_spreadsheet.id, simple_csv_data)

        sh = self.gc.open_by_key(new_spreadsheet.id)
        self.assertEqual(sh.sheet1.get_all_values(), rows)

        self.gc.del_spreadsheet(new_spreadsheet.id)

    def test_access_non_existing_spreadsheet(self):
        wks = self.gc.open_by_key("test")
        with self.assertRaises(APIError) as error:
            wks.worksheets()
        self.assertEqual(error.exception.args[0]["code"], 404)
        self.assertEqual(
            error.exception.args[0]["message"], "Requested entity was not found."
        )
        self.assertEqual(error.exception.args[0]["status"], "NOT_FOUND")

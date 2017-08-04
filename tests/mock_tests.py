"""A test suite that doesn't query the Google API.

Avoiding direct network access is benefitial in that it markedly speeds up
testing, avoids error-prone credential setup, and enables validation even if
internet access is unavailable.
"""
from datetime import datetime
import unittest
try:
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

import mock

import gspread
from tests import test
from tests import test_utils


class MockGspreadTest(unittest.TestCase):
    """This is the base class for all tests not accessing the API.

    IMPORTANT: This class must be inherited _BEFORE_ a test suite inheriting
    from GspreadTest. This allows MockGspreadTest.setUpClass to clobber the
    one inherited from GspreadTest which authorizes with the Google API.
    """

    @classmethod
    def setUpClass(cls):
        try:
            cls.config = ConfigParser.RawConfigParser()
            cls.gc = gspread.client.Client(auth={})
        except IOError as e:
            msg = "Can't find %s for reading test configuration. "
            raise Exception(msg % e.filename)


class MockClientTest(MockGspreadTest, test.ClientTest):
    """Test for gspread.Client that mocks out the server response."""

    @classmethod
    def setUpClass(cls):
        super(MockClientTest, cls).setUpClass()
        key = '0123456789ABCDEF'
        title = 'This is a spreadsheet title'
        url = 'https://docs.google.com/spreadsheet/ccc?key=' + key
        updated = datetime.now()
        dev_email = 'foobar@developer.gserviceaccount.com'
        user_name = 'First Last'
        user_email = 'real_email@gmail.com'

        # Initialize mock ConfigParser
        cls.config.add_section('Spreadsheet')
        cls.config.set('Spreadsheet', 'key', key)
        cls.config.set('Spreadsheet', 'title', title)
        cls.config.set('Spreadsheet', 'url', url)

        # Set up spreadsheet mock
        feed_obj = test_utils.SpreadsheetFeed(updated, dev_email)
        feed_obj.add_entry(key, title, user_name, user_email, updated)

        feed = feed_obj.to_xml()
        cls.gc.get_spreadsheets_feed = mock.Mock(return_value=feed)

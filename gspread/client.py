from xml.etree import ElementTree

from . import __version__
from .ns import _ns
from .httpsession import HTTPSession
from .models import Spreadsheet
from .exceptions import AuthenticationError, SpreadsheetNotFound

AUTH_SERVER = 'https://www.google.com'
SPREADSHEETS_SERVER = 'spreadsheets.google.com'

class Client(object):
    """A client class for communicating with Google's Date API.

    auth param is a tuple containing an email and a password.
    http_session is session object capable of making HTTP requests while
    persisting headers. Defaults to gspread.httpsession.HTTPSession.

    """
    def __init__(self, auth, http_session=None):
        self.auth = auth

        if not http_session:
            self.session = HTTPSession()

    def _get_auth_token(self, content):
        for line in content.splitlines():
            if line.startswith('Auth='):
                return line[5:]
        return None

    def login(self):
        """Authorize client using ClientLogin.

        This method is using API described at:
        http://code.google.com/apis/accounts/docs/AuthForInstalledApps.html

        """
        source = 'burnash-gspread-%s' % __version__
        service = 'wise'

        data = {'Email': self.auth[0],
                'Passwd': self.auth[1],
                'accountType': 'HOSTED_OR_GOOGLE',
                'service': service,
                'source': source}

        url = AUTH_SERVER + '/accounts/ClientLogin'

        r = self.session.post(url, data)
        content = r.read()

        if r.code == 200:
            token = self._get_auth_token(content)
            auth_header = "GoogleLogin auth=%s" % token
            self.session.add_header('Authorization', auth_header)

        elif r.code == 403:
            if content.strip() == 'Error=BadAuthentication':
                raise AuthenticationError("Incorrect username or password")
            else:
                raise AuthenticationError("Unable to authenticate. %s code" % r.code)
        else:
            raise AuthenticationError("Unable to authenticate. %s code" % r.code)

    def open(self, title):
        """Open a spreadsheet with specified title.

        If there's more than one spreadsheet with same title the first one
        will be opened.

        """
        feed = self.get_spreadsheets_feed()

        for elem in feed.findall(_ns('entry')):
            elem_title = elem.find(_ns('title')).text
            if elem_title.strip() == title:
                id_parts = elem.find(_ns('id')).text.split('/')
                key = id_parts[-1]
                return Spreadsheet(self, key)
        else:
            raise SpreadsheetNotFound

    def openall(self, title=None):
        """Open all spreadsheets.

        Return a list of all available spreadsheets.
        Can be filtered with title parameter.

        """
        feed = self.get_spreadsheets_feed()
        result = []
        for elem in feed.findall(_ns('entry')):
            id_parts = elem.find(_ns('id')).text.split('/')
            key = id_parts[-1]
            if title is not None:
                elem_title = elem.find(_ns('title')).text
                if elem_title.strip() != title:
                    continue
            result.append(Spreadsheet(self, key))

        return result

    def get_spreadsheets_feed(self, visibility='private', projection='full'):
        uri = ('https://%s/feeds/spreadsheets/%s/%s'
            % (SPREADSHEETS_SERVER, visibility, projection))

        r = self.session.get(uri)
        return ElementTree.fromstring(r.read())

    def get_worksheets_feed(self, key, visibility='private', projection='full'):
        uri = ('https://%s/feeds/worksheets/%s/%s/%s'
            % (SPREADSHEETS_SERVER, key, visibility, projection))

        r = self.session.get(uri)
        return ElementTree.fromstring(r.read())

    def get_cells_feed(self, key, worksheet_key, cell=None,
                       visibility='private', projection='full'):
        uri = ('https://%s/feeds/cells/%s/%s/%s/%s'
            % (SPREADSHEETS_SERVER, key, worksheet_key, visibility, projection))

        if cell != None:
            uri = '%s/%s' % (uri, cell)

        r = self.session.get(uri)
        return ElementTree.fromstring(r.read())

    def put_cell(self, url, data):
        headers = {'Content-Type': 'application/atom+xml'}
        data = "<?xml version='1.0' encoding='UTF-8'?>%s" % data
        r = self.session.put(url, data, headers=headers)

        return ElementTree.fromstring(r.read())

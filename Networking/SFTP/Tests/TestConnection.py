import unittest
from ProcessDocx.Networking.SftpData import *

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.test_sftp = SftpConnection()
        self.test_sftp.username__ = 'WMurphy'
        self.test_sftp.password__ = 'Tr2oy222222!'
        self.test_sftp.port__ = 22
        self.test_sftp.host__ = '10.1.48.58'
        self.test_sftp.local_path__ = 'N:\\USD\\Business Data and Analytics\\Will dev folder\\pickle_path'
        self.test_sftp.remote_path__ = '/home/wmurphy/pickle_files'

    def tearDown(self):
        del self.test_sftp

    def test_username(self):
        self.assertEqual(self.test_sftp.username__, 'WMurphy')

    def test_password(self):
        self.assertEqual(self.test_sftp.password__, 'Tr2oy222222!')

    def test_port(self):
        self.assertEqual(self.test_sftp.port__, 22)

    def test_host(self):
        self.assertEqual(self.test_sftp.host__, '10.1.48.58')

    def test_local_path(self):
        self.assertEqual(self.test_sftp.local_path__, 'N:\\USD\\Business Data and Analytics\\Will dev folder\\pickle_path')

    def test_remote_path(self):
        self.assertEqual(self.test_sftp.remote_path__, '/home/wmurphy/pickle_files')

    def test_connection(self):
        self.test_sftp.connect()
        self.assertEqual(self.test_sftp.is_connected, True)




if __name__ == '__main__':
    unittest.main()

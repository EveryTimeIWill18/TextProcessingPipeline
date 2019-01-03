# -*- coding: utf-8 -*-
import os
import glob
import socket
import socks
import paramiko
import zipfile
import logging
import threading
import shutil
import sshtunnel
import unicodedata
import pickle
from datetime import datetime

# Global variables
# ---------------------------------------------------------------------
CHUNK_SIZE = 100     # number of files to process
LOG_PATH = "C:\\Users\\WMurphy\\PycharmProjects\\DataProcessingPipeline\\logs\\SFTP_LOG.log"
LOCK = threading.Lock() # lock to ensure thread safety

def sftp_log(path, err_file):
    fmt_str =  '%(asctime)s - %(name)s - %(message)s'
    formatter = logging.Formatter(fmt_str)
    logging.basicConfig(filename=path, level=logging.INFO, format=fmt_str)
    logging.info("Test of logging info.")
    logging.critical("Test of logging critical.")
    logging.exception("Test of logging exceptions.")
    logging.error("File: {} could not be read".format(err_file))



class SftpCredentials(object):
    """
    SftpCredentials
    ==============
    Stores the sftp credentials that will be used
    to create an sftp connection.
    """

    def __init__(self):
        # private attributes
        # ------------------
        self.__username       = None
        self.__password       = None
        self.__host           = None
        self.__port           = None
        self.__local_path     = None
        self.__remote_path    = None

    @property
    def username__(self):
        pass
    @username__.setter
    def username__(self, un):
        self.__username = un
    @username__.getter
    def username__(self):
        return self.__username
    @username__.deleter
    def username__(self):
        del self.__username

    @property
    def password__(self):
        pass
    @password__.setter
    def password__(self, pw):
        self.__password = pw
    @password__.getter
    def password__(self):
        return self.__password
    @password__.deleter
    def password__(self):
        del self.__password

    @property
    def host__(self):
        pass
    @host__.setter
    def host__(self, h):
        self.__host = h
    @host__.getter
    def host__(self):
        return self.__host
    @host__.deleter
    def host__(self):
        del self.__host

    @property
    def port__(self):
        pass
    @port__.setter
    def port__(self, p):
        self.__port = p
    @port__.getter
    def port__(self):
        return self.__port
    @port__.deleter
    def port__(self):
        del self.__port

    @property
    def local_path__(self):
        pass
    @local_path__.setter
    def local_path__(self, lp):
        self.__local_path = lp
    @local_path__.getter
    def local_path__(self):
        return self.__local_path
    @local_path__.deleter
    def local_path__(self):
        del self.__local_path

    @property
    def remote_path__(self):
        pass
    @remote_path__.setter
    def remote_path__(self, rp):
        self.__remote_path = rp
    @remote_path__.getter
    def remote_path__(self):
        return self.__remote_path
    @remote_path__.deleter
    def remote_path__(self):
        del self.__remote_path



class DataTransfer:
    """
    DataTransfer
    ============
    Data that will be passed to the remote server.
    """
    def __init__(self):
        self.__name             = None
        self.__archive          = None
        self.__directory        = None
        self.__ext_type         = None

        self.files_             = []
        self.processed_files    = 0
        self.zipped_files       = 0

    @property
    def name__(self):
        pass
    @name__.setter
    def name__(self, n):
        self.__name = n
    @name__.getter
    def name__(self):
        return self.__name
    @name__.deleter
    def name__(self):
        del self.__name

    @property
    def archive__(self):
        pass
    @archive__.setter
    def archive__(self, ar):
        if self.name__ is not None:
            self.__archive = None
    @archive__.getter
    def archive__(self):
        return self.__archive
    @archive__.deleter
    def archive__(self):
        del self.__archive

    @property
    def directory__(self):
        pass
    @directory__.setter
    def directory__(self, d):
        self.__directory = d
    @directory__.getter
    def directory__(self):
        return self.__directory
    @directory__.deleter
    def directory__(self):
        del self.__directory

    @property
    def ext_type__(self):
        pass
    @ext_type__.setter
    def ext_type__(self, ext_type):
        self.__ext_type = ext_type
    @ext_type__.getter
    def ext_type__(self):
        return self.__ext_type
    @ext_type__.deleter
    def ext_type__(self):
        del self.__ext_type

    def files__(self):
        try:
            if self.directory__ is not None:
                os.chdir(self.directory__)
                self.files_ = glob.glob('*.{}'.format(self.ext_type__))
                print("Number of docx files: {}".format(len(self.files_)))
            else:
                raise OSError('OSError: Directory, {} not found'.format(self.directory__))
        except OSError as e:
            print(e)
        finally:
            pass

    def copy_files(self, local_dir):
        """
        Copy files to a local directory.
        :return:
        """
        try:
            if len(self.files_) > 0:
                if os.path.exists(local_dir):
                    for f in self.files_:
                        try:
                            shutil.copy(f, local_dir)
                            self.processed_files += 1
                        except:
                            sftp_log(LOG_PATH, f)
                        finally:
                            pass
        except ValueError:
            print("No files found.")
        finally:
            pass


    def build_archive(self, file_path, archive_name, extension):
        """
        Create an archived directory to transfer data.
        :param archive_location:
        :return:
        """
        archive = zipfile.ZipFile(archive_name, 'w')
        if os.path.exists(file_path):
            os.chdir(file_path)
            print("Current Directory: {}".format(file_path))
            file_counter = 0
            files = glob.glob('*.{}'.format(extension))
            if len(files) > 0:
                for f in files:
                    try:
                        archive.write(os.path.join(os.getcwd(), f))
                        file_counter += 1
                    except:
                        print("WriteError: error writing {} to archive".format(files))
                    finally:
                        print("Number of files added to archive: {}".format(file_counter))
            else:
                return "No files of extension {} found".format(extension)


class SftpConnection(SftpCredentials, DataTransfer):
    """
    SftpConnection
    ==============
    Create a secure file transfer protocol connection.
    SftpConnection inherits from the SftpCredentials
    superclass.
    """

    def __init__(self):
        SftpCredentials.__init__(self) # initialize super-class
        DataTransfer.__init__(self)    # initialize super-class

        self.sock = socks.socksocket() # current socket connection
        self.sftp    = None
        self.client  = None
        self.is_connected = False

    def connect(self):
        """
        Connect to remote server.
        :return:
        """
        try:
            assert self.host__     is not None
            assert self.port__     is not None
            assert self.username__ is not None
            assert self.password__ is not None
            #print("host = {}".format(self.host__()))
            # set proxy connection values
            self.sock.set_proxy(
                proxy_type=None,
                addr=self.host__,
                port=self.port__,
                username=self.username__,
                password=self.password__
            )
            # connect the socket
            self.sock.connect((self.host__, self.port__))
            if socket.gethostname() is not None:
                print("Connection Successful:\nHost: {}".format(socket.gethostname()))

                # create transport
                self.sftp = paramiko.Transport(self.sock)
                try:
                    self.sftp.connect(
                        username=self.username__,
                        password=self.password__
                    )
                    if self.sftp.is_alive():
                        print("Transport is live.")
                        self.is_connected = True
                        # create client
                        self.client = paramiko.SFTPClient.from_transport(self.sftp)

                        # load in the files to be transferred
                        assert self.directory__ is not None
                        assert len(self.files_) > 0
                        #self.copy_files("C:\\Users\\WMurphy\\PycharmProjects\\DataProcessingPipeline\\docx_files")
                        self.build_archive('C:\\Users\\WMurphy\\PycharmProjects\\DataProcessingPipeline')

                except:
                    pass
        except:
            pass
        finally:
            pass




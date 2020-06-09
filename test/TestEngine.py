# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from Templatomatic.TemplatomaticServer import MethodContext
from Templatomatic.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil
from Templatomatic.MakeTemplates import LogMixin


class TestBase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        te = TestEngine.get_instance()
        if not te.env_set_up:
            te.set_up_test_env()

        cls.te = te
        # copy over the attributes
        attrs = [
            'cfg', 'ctx',
            'wsClient', 'wsName', 'ws_id',
            'dfu',
            'scratch',
        ]

        for attr in attrs:
            setattr(cls, attr, getattr(te, attr))


class TestEngine(LogMixin, object):

    __instance = None

    @staticmethod
    def get_instance():
        if TestEngine.__instance is None:
            TestEngine()
        return TestEngine.__instance

    def __init__(self):
        """ Virtually private constructor. """
        if TestEngine.__instance is not None:
            raise Exception("Please use 'get_instance' to init the test engine")
        else:
            TestEngine.__instance = self
            self.env_set_up = False

    def set_up_test_env(self):

        self.logger.info('setting up test environment...')
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        suffix = int(time.time() * 1000)

        self.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('Templatomatic'):
            self.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = self.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        self.ctx = MethodContext(None)
        self.ctx.update({
            'token': token,
            'user_id': user_id,
            'provenance': [{
                'service': 'kb_Msuite',
                'method': 'please_never_use_it_in_production',
                'method_params': []
            }],
            'authenticated': 1
        })
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = self.cfg['scratch']
        self.appdir = self.cfg['appdir']

        self.wsURL = self.cfg['workspace-url']
        self.wsClient = Workspace(self.wsURL)
        self.wsName = "test_Templatomatic_" + str(suffix)
        self.ws_info = self.wsClient.create_workspace({'workspace': self.wsName})
        self.ws_id = self.ws_info[6]
        self.dfu = DataFileUtil(self.callback_url)

        self.logger.info('set up new workspace: ' + self.wsName)

        self.env_set_up = True
        self.logger.info('Finished test environment set up')

    def clean_up_test_env(self):
        if hasattr(self, 'wsName'):
            self.wsClient.delete_workspace({'workspace': self.wsName})
            self.logger.info('Test workspace was deleted')

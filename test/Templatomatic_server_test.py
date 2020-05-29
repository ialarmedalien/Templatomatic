# -*- coding: utf-8 -*-
import os
import time
import unittest
from configparser import ConfigParser

from Templatomatic.TemplatomaticImpl import Templatomatic
from Templatomatic.TemplatomaticServer import MethodContext
from Templatomatic.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil


class Templatomatic_server_test(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        token = os.environ.get('KB_AUTH_TOKEN', None)
        config_file = os.environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('Templatomatic'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({
            'token': token,
            'user_id': user_id,
            'provenance': [{
                'service': 'Templatomatic',
                'method': 'please_never_use_it_in_production',
                'method_params': []
            }],
            'authenticated': 1
        })
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.wsURL = cls.cfg['workspace-url']
        cls.wsClient = Workspace(cls.wsURL)
        cls.dfu = DataFileUtil(cls.callback_url)
        cls.serviceImpl = Templatomatic(cls.cfg)
        suffix = int(time.time() * 1000)
        cls.wsName = "test_Templatomatic_" + str(suffix)
        cls.wsClient.create_workspace({'workspace': cls.wsName})

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa

    def check_created_report(self, result):
        """ basic checks on a created report
        Args:
          result: output from report creation call
        Return:
          object data from created report
        """
        self.assertEqual(self.serviceImpl.status(self.ctx)[0]['state'], 'OK')
        self.assertTrue(len(result[0]['report_ref']))
        self.assertTrue(len(result[0]['report_name']))
        obj = self.dfu.get_objects({'object_refs': [result[0]['report_ref']]})
        return obj['data'][0]['data']

    def check_extended_result(self, result, link_name, file_names):
        """
        Test utility: check the file upload results for an extended report
        Args:
          result - result dictionary from running .create_extended_report
          link_name - one of "html_links" or "file_links"
          file_names - names of the files for us to check against
        Returns:
            obj - report object created
        """
        obj = self.check_created_report(result)
        file_links = obj[link_name]
        self.assertEqual(len(file_links), len(file_names))
        # Test that all the filenames listed in the report object map correctly
        saved_names = set([str(f['name']) for f in file_links])
        self.assertEqual(saved_names, set(file_names))
        return obj

    def test_run_Templatomatic(self):

        result = self.serviceImpl.run_Templatomatic(self.ctx, {
            'workspace_name': self.wsName,
        })
        self.check_extended_result(result, 'html_links', [
            'tsv_report.html',
            'json_report.html',
            'standalone_aoa_report.html',
            'standalone_aoo_report.html',
        ])


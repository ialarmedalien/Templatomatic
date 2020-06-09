# -*- coding: utf-8 -*-
from TestEngine import TestBase
from Templatomatic.TemplatomaticImpl import Templatomatic
from shutil import rmtree

class TestTemplatomatic(TestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.serviceImpl = Templatomatic(cls.cfg)

    def tearDown(self):
        # clean out self.scratch
        rmtree(self.scratch)


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

    def test_run_Templatomatic_single_table(self):

        result = self.serviceImpl.run_Templatomatic(self.ctx, {
            'workspace_id': self.ws_id,
            'workspace_name': self.wsName,
            'report_type': 'single_table',
        })
        self.check_extended_result(result, 'html_links', [
            'tsv_report.html',
            'json_report.html',
            'standalone_aoa_report.html',
            'standalone_aoo_report.html',
        ])


    def test_run_Templatomatic_table_and_image(self):

        result = self.serviceImpl.run_Templatomatic(self.ctx, {
            'workspace_id': self.ws_id,
            'workspace_name': self.wsName,
            'report_type': 'table_and_image',
        })
        self.check_extended_result(result, 'html_links', [
            'table_remote_image_report.html',
            'table_local_image_report.html',
        ])

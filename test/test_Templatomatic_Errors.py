# -*- coding: utf-8 -*-
from TestEngine import TestBase
from Templatomatic.TemplatomaticImpl import Templatomatic

class TestTemplatomaticErrors(TestBase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.serviceImpl = Templatomatic(cls.cfg)

    def test_no_params(self):
        err_str = 'Missing required parameters workspace_id and report_type'

        with self.assertRaisesRegex(ValueError, err_str):
            self.serviceImpl.run_Templatomatic(self.ctx, {})

        with self.assertRaisesRegex(ValueError, err_str):
            self.serviceImpl.run_Templatomatic(self.ctx, None)


    def test_invalid_params(self):

        err_str = 'Required parameter workspace_id is not set or is invalid'

        with self.assertRaisesRegex(ValueError, err_str):
            self.serviceImpl.run_Templatomatic(self.ctx, {'this': 'that'})

        with self.assertRaisesRegex(ValueError, err_str):
            self.serviceImpl.run_Templatomatic(self.ctx, {
                'workspace_id': None,
            })

        with self.assertRaisesRegex(ValueError, err_str):
            self.serviceImpl.run_Templatomatic(self.ctx, {
                'workspace_id': '',
            })


    def test_invalid_report_type_params(self):
        '''
        test invalid report type params
        '''

        err_str = 'Required parameter report_type is not set or is invalid'

        for input in [None, '', '12345', 'test_string']:
            with self.assertRaisesRegex(ValueError, err_str):
                self.serviceImpl.run_Templatomatic(self.ctx, {
                    'workspace_id': self.ws_id,
                    'report_type': input,
                })


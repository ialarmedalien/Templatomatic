# -*- coding: utf-8 -*-
import logging
import os
import json
from shutil import copy, copytree
from installed_clients.KBaseReportClient import KBaseReport


class LogMixin(object):
    @property
    def logger(self):
        # name = '.'.join([__name__, self.__class__.__name__])
        class_name = self.__class__.__name__
        return logging.getLogger('Templatomatic.' + class_name)


class MakeTemplates(LogMixin, object):
    '''
    Module Name:
    MakeTemplates

    Module Description:
    A module for making templates
    '''

    def __init__(self, config):
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.scratch = config['scratch']
        self.appdir = config['appdir']
        logging.basicConfig(
            format='%(name)s %(levelname)s %(message)s',
            level=logging.DEBUG
        )
        self.reporter = KBaseReport(self.callback_url, service_ver='dev')

    def make_templates(self, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output

        # copy the templates into 'scratch', where they can be accessed by KBaseReport
        copytree(
            os.path.join(self.appdir, 'templates'),
            os.path.join(self.scratch, 'templates')
        )

        html_links = [
            self.report_in_directory(),
            self.standalone_report_from_tsv(),
        ]

        result = self.reporter.create_extended_report({
            'html_links': html_links,
            'direct_html_link_index': 0,
            'report_object_name': 'My_Cool_Report',
            'workspace_name': params['workspace_name']
        })

        self.logger.debug({'combined report': result})
        return result

    def standalone_report_from_tsv(self):
        '''
        render a report from some standalone data
        '''

        source_file = os.path.join(self.appdir, 'data', 'edge_data.tsv')

        # read in a file, splitting on '\n' and then '\t' to create a list of lists
        with open(source_file, 'r') as read_fh:
            lines = list(map(lambda x: x.split('\t'), read_fh.read().rstrip().split('\n')))

        tmpl_data = {
            # lines[0] is the header
            # the rest of the lines are the data points
            'parsed_data_from_file': lines[1:],
        }

        result = {
            'name': 'standalone_report.html',
            'template': {
                'template_file': os.path.join(self.scratch, 'templates', 'edge_data_array.tt'),
                'template_data_json': json.dumps(tmpl_data),
            },
            'description': 'HTML report with data from controller',
        }

        self.logger.debug({'extended_report': result})

        return result

    def report_in_directory(self):
        '''
        render a report in a directory with supporting files
        '''

        # copy the templates into the scratch directory
        output_dir = os.path.join(self.scratch, 'output_dir')
        os.makedirs(output_dir)

        # first render the report
        result = self.reporter.render_template({
            'template_file': os.path.join(self.scratch, 'templates', 'edge_data_tsv_file.tt'),
            'template_data_json': json.dumps({
                'file_path': 'edge_data.tsv',
            }),
            'output_file': os.path.join(output_dir, 'report.html')
        })

        self.logger.debug({'render_template': result})

        # copy any supporting files into the directory
        # these might also include images, JS, or CSS files needed to render the page,
        # as well as data files
        copy(
            os.path.join(self.appdir, 'data', 'edge_data.tsv'),
            os.path.join(output_dir, 'edge_data.tsv')
        )

        # add the directory containing the report and supporting files to html_links
        return {
            'path': output_dir,
            'name': 'report.html',
            'description': 'HTML report in directory with supporting files',
        }

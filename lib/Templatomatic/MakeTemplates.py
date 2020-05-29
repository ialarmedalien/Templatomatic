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
        '''
        create HTML reports from templates using a variety of methods
        '''
        self.logger.info({'KBaseReport version': self.reporter._service_ver})

        # copy the templates into 'scratch', where they can be accessed by KBaseReport
        copytree(
            os.path.join(self.appdir, 'templates'),
            os.path.join(self.scratch, 'templates')
        )

        html_links = [
            self.create_report_in_directory('json'),
            self.create_report_in_directory('tsv'),
            self.standalone_report_array_of_arrays(),
            self.standalone_report_array_of_objects(),
        ]

        result = self.reporter.create_extended_report({
            'html_links': html_links,
            'direct_html_link_index': 0,
            'report_object_name': 'My_Cool_Report',
            'workspace_name': params['workspace_name']
        })

        self.logger.debug({'combined report': result})
        return {
            'report_name': result['name'],
            'report_ref':  result['ref'],
        }

    def standalone_report_array_of_arrays(self):
        '''
        render a report with an array of arrays as table data
        '''

        source_file = os.path.join(self.appdir, 'data', 'edge_data.tsv')

        # read in a file, splitting on '\n' and then '\t' to create a list of lists
        with open(source_file, 'r') as read_fh:
            lines = list(map(lambda x: x.split('\t'), read_fh.read().rstrip().split('\n')))

        tmpl_data = {
            # lines[0] is the header
            # the rest of the lines are the data points
            'data_array_of_arrays': lines[1:],
        }

        return {
            'name': 'standalone_aoa_report.html',
            'template': {
                'template_file': os.path.join(self.scratch, 'templates', 'edge_data_array.tt'),
                'template_data_json': json.dumps(tmpl_data),
            },
            'description': 'HTML report with data from controller',
        }

    def standalone_report_array_of_objects(self):
        '''
        render a report with an array of objects (dicts) as table data
        '''

        source_file = os.path.join(self.appdir, 'data', 'edge_data.json')

        # read in JSON data
        with open(source_file, 'r') as read_fh:
            lines = read_fh.read().rstrip()

        tmpl_data = {
            'data_array_of_objects': json.loads(lines),
        }

        return {
            'name': 'standalone_aoo_report.html',
            'template': {
                'template_file': os.path.join(self.scratch, 'templates', 'edge_data_object.tt'),
                'template_data_json': json.dumps(tmpl_data),
            },
            'description': 'HTML report with data from controller',
        }

    def create_report_in_directory(self, file_format):
        '''
        Create a report that runs off a data file in format `file_format`
        
        The report HTML page must be rendered first, and then the rendered page supplied, along with the data file and any other supporting files, as a directory to KBaseReport. This allows HTML links to files in that directory to work correctly.
        '''
        output_dir = os.path.join(self.scratch, file_format + '_output_dir')
        report_file = file_format + '_report.html'
        data_file = 'edge_data.' + file_format
        template_file = 'edge_data_' + file_format + '_file.tt'
        report_description = 'HTML report, ' + file_format + ' data source, in directory with supporting files'

        # create the output directory
        os.makedirs(output_dir)

        # render the report template
        result = self.reporter.render_template({
            'template_file': os.path.join(self.scratch, 'templates', template_file),
            'template_data_json': json.dumps({
                'file_path': data_file,
            }),
            'output_file': os.path.join(output_dir, report_file)
        })

        # copy any supporting files into the directory
        # these might also include images, JS, or CSS files needed to render the page,
        # as well as data files
        copy(
            os.path.join(self.appdir, 'data', data_file),
            os.path.join(output_dir, data_file)
        )

        # add the directory containing the report and supporting files to html_links
        return {
            'path': output_dir,
            'name': report_file,
            'description': report_description,
        }

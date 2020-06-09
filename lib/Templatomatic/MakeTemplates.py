# -*- coding: utf-8 -*-
import logging
import os
import json
from html import escape
from shutil import copy, copytree
from installed_clients.KBaseReportClient import KBaseReport


class LogMixin(object):
    @property
    def logger(self):
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


    def edge_data_cols(self):
        '''
        definition of table columns for DataTables.js
        '''

        return [
          { 'data': 'node1',              'title': 'Source node' },
          { 'data': 'node2',              'title': 'Target node' },
          { 'data': 'edge',               'title': 'Edge weight' },
          { 'data': 'edge_descrip',       'title': 'Edge description' },
          { 'data': 'layer_descrip',      'title': 'Layer description' },
        ]


    def read_template(self, template_name):
        '''
        read in a template file and escape all html content

        used to display template contents
        '''

        with open(os.path.join(self.appdir, 'templates', template_name)) as file:
            lines = file.read()

        # escape all the html, display the results
        escaped_lines = escape(lines, quote=True)

        return escaped_lines


    def validate_params(self, params):

        if not params:
            raise ValueError('Missing required parameters workspace_id and report_type')

        if 'workspace_id' not in params or not params['workspace_id']:
            raise ValueError('Required parameter workspace_id is not set or is invalid');

        valid_report_types = [ 'single_table', 'table_and_image' ]

        if 'report_type' not in params or params['report_type'] not in valid_report_types:
            raise ValueError('Required parameter report_type is not set or is invalid')


    def make_templates(self, params):
        '''
        create HTML reports from templates using a variety of methods
        '''

        self.validate_params(params)

        self.logger.info({'KBaseReport version': self.reporter._service_ver})

        # copy the templates into 'scratch', where they can be accessed by KBaseReport
        copytree(
            os.path.join(self.appdir, 'templates'),
            os.path.join(self.scratch, 'templates')
        )

        if params['report_type'] == 'single_table':
            html_links = [
                self.create_report_in_directory('json'),
                self.create_report_in_directory('tsv'),
                self.standalone_report_array_of_arrays(),
                self.standalone_report_array_of_objects(),
            ]
        elif params['report_type'] == 'table_and_image':
            html_links = [
                self.table_and_image_report_local_files(),
                self.table_and_image_report_no_files(),
            ]

        result = self.reporter.create_extended_report({
            'html_links': html_links,
            'direct_html_link_index': 0,
            'report_object_name': 'My_Cool_Report',
            'workspace_name': params['workspace_name'],
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
        template_file = os.path.join(self.scratch, 'templates', 'edge_data.tt')

        # read in a file, splitting on '\n' and then '\t' to create a list of lists
        with open(source_file, 'r') as read_fh:
            lines = list(map(lambda x: x.split('\t'), read_fh.read().rstrip().split('\n')))

        tmpl_data = {
            'page_title': 'Edge Data Table, from an array of arrays',
            'table_tab_title': 'Edge Data',
            # lines[0] is the header line
            # the rest of the lines are the data points
            'data_array': lines[1:],
            # formatted column names in the order they appear in the header line
            'cols': [
              { 'title': 'Source node' },
              { 'title': 'Target node' },
              { 'title': 'Edge weight' },
              { 'title': 'Edge description' },
              { 'title': 'Layer description' },
            ],
        }

        # for debugging
        tmpl_data['tmpl_vars'] = json.dumps(tmpl_data, sort_keys=True, indent=2)
        tmpl_data['template_content'] = self.read_template(template_file)

        return {
            'name': 'standalone_aoa_report.html',
            'template': {
                'template_file': template_file,
                'template_data_json': json.dumps(tmpl_data),
            },
            'description': 'HTML report with data from controller',
        }


    def standalone_report_array_of_objects(self):
        '''
        render a report with an array of objects (dicts) as table data
        '''

        template_file = os.path.join(self.scratch, 'templates', 'edge_data.tt')
        edge_data_object_array = self._get_json_report_data()

        tmpl_data = {
            'page_title':       'Edge Data Table, from an array of objects',
            'table_tab_title':  'Edge Data',
            'data_array':       edge_data_object_array,
            # our data is in the form of an array of objects [dicts] with the key/value pairs that
            # appeared in the original file. To make it more viewer-friendly, remap the
            # names in the object to appropriate column headers
            'cols':             self.edge_data_cols(),
        }

        # for debugging
        tmpl_data['tmpl_vars'] = json.dumps(tmpl_data, sort_keys=True, indent=2)
        tmpl_data['template_content'] = self.read_template(template_file)

        return {
            'name': 'standalone_aoo_report.html',
            'template': {
                'template_file': template_file,
                'template_data_json': json.dumps(tmpl_data),
            },
            'description': 'HTML report with data from controller',
        }


    def create_report_in_directory(self, file_format):
        '''
        Create a report that runs off a data file in format `file_format`

        The report HTML page must be rendered first, and then the rendered page supplied,
        along with the data file and any other supporting files, as a directory to KBaseReport.
        This allows HTML links to files in that directory to work correctly.
        '''
        output_dir = os.path.join(self.scratch, file_format + '_output_dir')
        report_file = file_format + '_report.html'
        data_file = 'edge_data.' + file_format
        template_file = os.path.join(self.scratch, 'templates', 'edge_data.tt')
        report_description = 'HTML report, ' + file_format + ' data source, with supporting files'

        tmpl_data = {
          'page_title':       'Edge Table, data from a ' + file_format + ' file',
          'table_tab_title':  'Edge Data',
          'data_file':        data_file,
          'data_file_format': file_format,
          'cols':             self.edge_data_cols(),
        }

        tmpl_data['tmpl_vars'] = json.dumps(tmpl_data, sort_keys=True, indent=2)
        tmpl_data['template_content'] = self.read_template(template_file)

        # create the output directory
        os.makedirs(output_dir)

        # render the report template
        result = self.reporter.render_template({
            'template_file': template_file,
            'template_data_json': json.dumps(tmpl_data),
            'output_file': os.path.join(output_dir, report_file)
        })

        self.logger.info(result)

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


    def table_and_image_report_local_files(self):
        '''
        Create a report with two tabs, one containing tabular data, and the other, a captioned image.

        If a local image is used (e.g. output from an app), the report HTML page must be rendered
        first, and then the rendered page supplied, along with the image file, as a directory to
        KBaseReport.
        '''

        output_dir = os.path.join(self.scratch, 'table_image_output_dir')
        report_file = 'table_local_image_report.html'
        template_file = os.path.join(self.scratch, 'templates', 'table_and_image_tabs.tt')
        report_description = 'HTML report, table and image tabs, with supporting files'

        # local image file
        local_image_file = 'logo.png'
        local_image_caption = '<p>The <a href="http://kbase.us">KBase logo</a>, in PNG format. This file was uploaded as part of the report.</p>'

        # data for the table
        edge_data_object_array = self._get_json_report_data()

        # remote image file
        tmpl_data = {
          'page_title':             'Edge Table and Image Report',
          'table_tab_title':        'Edge Data, from an array of objects',
          'data_array':             edge_data_object_array,
          'cols':                   self.edge_data_cols(),
          # image information
          'image_tab_title':        'Local image',
          'image_config_img_src':   local_image_file,
          'image_config_img_alt':   'KBase logo',
          'image_config_caption':   local_image_caption,
        }

        # for debugging
        tmpl_data['tmpl_vars'] = json.dumps(tmpl_data, sort_keys=True, indent=2)
        tmpl_data['template_content'] = self.read_template(template_file)

        # create the output directory
        os.makedirs(output_dir)

        # render the report template
        result = self.reporter.render_template({
            'template_file': template_file,
            'template_data_json': json.dumps(tmpl_data),
            'output_file': os.path.join(output_dir, report_file)
        })

        self.logger.info(result)

        # copy any supporting files into the directory
        # these might also include images, JS, or CSS files needed to render the page,
        # as well as data files
        copy(
            os.path.join(self.appdir, 'data', local_image_file),
            os.path.join(output_dir, local_image_file)
        )

        # add the directory containing the report and supporting files to html_links
        return {
            'path': output_dir,
            'name': report_file,
            'description': report_description,
        }


    def table_and_image_report_no_files(self):
        '''
        Create a report with two tabs, one containing tabular data, and the other, a captioned image.

        This report does not use any local files, so the template does not need to be rendered in
        advance.
        '''

        report_file = 'table_remote_image_report.html'
        template_file = os.path.join(self.scratch, 'templates', 'table_and_image_tabs.tt')
        report_description = 'HTML report, table and image tabs, with supporting files'

        # image file hosted elsewhere
        remote_image_file = 'https://kbase.github.io/kb_sdk_docs/_static/logo.png'
        remote_image_caption = '<p>The <a href="http://kbase.us">KBase logo</a>, in PNG format. This file is hosted on kbase.github.io</p>'

        edge_data_object_array = self._get_json_report_data()

        # remote image file
        tmpl_data = {
          'page_title':             'Edge Table and Image Report',
          'table_tab_title':        'Edge Data, from an array of objects',
          'data_array':             edge_data_object_array,
          'cols':                   self.edge_data_cols(),
          # image information
          'image_tab_title':        'Remote image',
          'image_config_img_src':   remote_image_file,
          'image_config_img_alt':   'KBase logo',
          'image_config_caption':   remote_image_caption,
        }

        # for debugging
        tmpl_data['tmpl_vars'] = json.dumps(tmpl_data, sort_keys=True, indent=2)
        tmpl_data['template_content'] = self.read_template(template_file)

        # add the directory containing the report and supporting files to html_links
        return {
            'template': {
                'template_file': template_file,
                'template_data_json': json.dumps(tmpl_data),
            },
            'name': report_file,
            'description': report_description,
        }


    def _get_json_report_data(self):
        '''
        read in a JSON file containing edge data as an array of JSON objects
        '''

        source_file = os.path.join(self.appdir, 'data', 'edge_data.json')

        # read in lines and parse the JSON to convert to py data structures (list of dicts)
        with open(source_file, 'r') as read_fh:
            lines = read_fh.read().rstrip()

        return json.loads(lines)

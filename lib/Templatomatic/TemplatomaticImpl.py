# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os
from Templatomatic.MakeTemplates import MakeTemplates
#END_HEADER


class Templatomatic:
    '''
    Module Name:
    Templatomatic

    Module Description:
    A KBase module: Templatomatic
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/ialarmedalien/Templatomatic.git"
    GIT_COMMIT_HASH = "f67a87248d06d51afaa6647e0e1c2e9eb6b8727d"

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        self.templater = MakeTemplates(config)
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass


    def run_Templatomatic(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_Templatomatic
        output = self.templater.make_templates(params)
        #END run_Templatomatic

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_Templatomatic return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]

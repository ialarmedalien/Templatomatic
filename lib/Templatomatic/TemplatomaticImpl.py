# -*- coding: utf-8 -*-
# BEGIN_HEADER
import logging
import os
from Templatomatic.MakeTemplates import MakeTemplates

# END_HEADER


class Templatomatic:
    """
    Module Name:
    Templatomatic

    Module Description:
    A KBase module: Templatomatic
    """

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.2"
    GIT_URL = "https://github.com/ialarmedalien/Templatomatic.git"
    GIT_COMMIT_HASH = "48e77e56392ac4bab9c8ffa605e99f145c7f574b"

    # BEGIN_CLASS_HEADER
    # END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        # BEGIN_CONSTRUCTOR
        self.callback_url = os.environ["SDK_CALLBACK_URL"]
        self.shared_folder = config["scratch"]
        self.templater = MakeTemplates(config)

        logging.basicConfig(
            format="%(name)s %(levelname)s %(message)s", level=logging.DEBUG
        )
        self.logger = logging.getLogger("Templatomatic." + self.__class__.__name__)

        # END_CONSTRUCTOR
        pass

    def run_Templatomatic(self, ctx, params):
        """
        This example function may look simple and generic, but it does something super cool involving templates and reports. Run it and see!
        :param params: instance of type "TemplatomaticInput" -> structure:
           parameter "report_type" of String
        :returns: instance of type "ReportResults" -> structure: parameter
           "name" of String, parameter "ref" of String
        """
        # ctx is the context object
        # return variables are: output
        # BEGIN run_Templatomatic
        self.logger.info({"params": params})
        output = self.templater.make_templates(params)

        # END run_Templatomatic

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError(
                "Method run_Templatomatic return value "
                + "output is not type dict as required."
            )
        # return the results
        return [output]

    def status(self, ctx):
        # BEGIN_STATUS
        returnVal = {
            "state": "OK",
            "message": "It's five o'clock somewhere.",
            "version": self.VERSION,
            "git_url": self.GIT_URL,
            "git_commit_hash": self.GIT_COMMIT_HASH,
        }
        # END_STATUS
        return [returnVal]

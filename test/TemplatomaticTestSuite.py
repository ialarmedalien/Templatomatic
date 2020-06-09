import unittest
import logging

from TestEngine import TestEngine
from test_Templatomatic import TestTemplatomatic
from test_Templatomatic_Errors import TestTemplatomaticErrors


if __name__ == '__main__':

    print("RUNNING MAIN!!!")

    # init logger
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(name)s %(levelname)s %(message)s'
    )

    te = TestEngine()
    te.set_up_test_env()
    te.logger.info('test env status: ' + str(te.env_set_up))

    test_loader = unittest.TestLoader()
    test_classes = [
        TestTemplatomatic,
        TestTemplatomaticErrors,
    ]

    suites = [test_loader.loadTestsFromTestCase(test_class) for test_class in test_classes]

    all_tests = unittest.TestSuite(suites)
    unittest.TextTestRunner(verbosity=3).run(all_tests)
    te.clean_up_test_env()

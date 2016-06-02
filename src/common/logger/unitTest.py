import unittest
from time import sleep

from common.logger import logger
from common.logger.logger import Logger

# @cond doxygen_unittest
class Test_Module(unittest.TestCase):


    def test_basic(self):
        log = Logger(name='Test1')
        log.setLevel(logger.WARNING)
        log.info('ERROR If you see this')
        log.debug('ERROR If you see this')
        log.warn('You should see this 1/5')
        log.warning('You should see this 2/5')
        log.error('You should see this 3/5')
        log.fatal('You should see this 4/5')
        log.critical('You should see this 5/5')
        pass

    def test_basic2(self):


        log = Logger()
        log.setLevel(logger.INFO)
        log.info('With default channel name (unitTest)')

        pass

if __name__ == '__main__':
    unittest.main()
## @endcond

import unittest
from time import sleep
from cStringIO import StringIO
import sys


from common.logger import logger
from common.logger.logger import Logger

# @cond doxygen_unittest
class Test_Module(unittest.TestCase):

    def setUp(self):
        sys.stderr = self.testOut = StringIO()

    def tearDown(self):
        sys.stderr = sys.__stderr__
        print self.testOut.getvalue()
        self.testOut.close()

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

        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 5)
        self.assertIn('Test1', logLines[0])

        pass

    def test_defaultLogName(self):
        log = Logger()
        log.setLevel(logger.INFO)
        log.info('With default channel name')

        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 1)
        # Verify the log name is unitTest (the default)
        self.assertIn('unitTest', logLines[0])
        pass

    def test_INFOLevel(self):
        log = Logger(name='Test1')
        log.setLevel(logger.INFO)
        log.warn('You should see this 1/6')
        log.warning('You should see this 2/6')
        log.error('You should see this 3/6')
        log.fatal('You should see this 4/6')
        log.critical('You should see this 5/6')
        log.info('You should see this 6/6')
        log.debug('You NOT see this')


        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 6)
        self.assertIn('Test1', logLines[0])

        pass

    def test_ChangeLevel(self):
        log = Logger(name='Test1')
        log.setLevel(logger.WARN)
        log.warn('You should see this 1/6')
        log.warning('You should see this 2/6')
        log.error('You should see this 3/6')
        log.fatal('You should see this 4/6')
        log.critical('You should see this 5/6')
        log.info('You NOT see this')
        log.debug('You NOT see this')
        log.setLevel(logger.INFO)
        log.info('You should see this 6/6')


        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 6)
        self.assertIn('Test1', logLines[0])

        pass

    def test_IniDefaultLevel(self):
        log = Logger()
        log.warn('You should see this 1/6')
        log.warning('You should see this 2/6')
        log.error('You should see this 3/6')
        log.fatal('You should see this 4/6')
        log.critical('You should see this 5/6')
        log.info('You should see this 6/6')
        log.debug('You NOT see this')

        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 6)
        self.assertIn('unitTest', logLines[0])

        pass

    def test_IniStringLevel(self):
        log = Logger(name='StringLevelTest')
        log.warn('You should NOT see this')
        log.warning('You should NOT see this')
        log.error('You should see this 1/3')
        log.fatal('You should see this 2/3')
        log.critical('You should see this 3/3')
        log.info('You should NOT see this')
        log.debug('You should NOT see this')

        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 3)
        self.assertIn('StringLevelTest', logLines[0])

        pass

    def test_IniIntegerLevel(self):
        log = Logger(name='StringIntTest')
        log.warn('You should NOT see this')
        log.warning('You should NOT see this')
        log.error('You should see this 1/3')
        log.fatal('You should see this 2/3')
        log.critical('You should see this 3/3')
        log.info('You should NOT see this')
        log.debug('You should NOT see this')

        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 3)
        self.assertIn('StringIntTest', logLines[0])

        pass

    def test_IniUnknownINILevel(self):
        log = Logger(name='StringUnknownTest')
        log.warn('You should see this 1/7')
        log.warning('You should see this 2/7')
        log.error('You should see this 3/7')
        log.fatal('You should see this 4/7')
        log.critical('You should see this 5/7')
        log.info('You should see this 6/7')
        log.debug('You should see this 7/7')
        log.setLevel(logger.INFO)

        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 8)
        self.assertIn('StringUnknownTest', logLines[0])
        self.assertIn('Unknown Log Level', logLines[0])
        pass

    def test_IniUnknownSetLevel(self):
        log = Logger()
        log.setLevel('notValid')
        log.warn('You should see this 1/7')
        log.warning('You should see this 2/7')
        log.error('You should see this 3/7')
        log.fatal('You should see this 4/7')
        log.critical('You should see this 5/7')
        log.info('You should see this 6/7')
        log.debug('You should see this 7/7')

        logLines = self.testOut.getvalue().strip().split('\n')
        self.assertEqual(len(logLines), 8)
        self.assertIn('unitTest', logLines[0])
        self.assertIn('Unknown Log Level', logLines[0])
        pass




if __name__ == '__main__':
    unittest.main()
## @endcond

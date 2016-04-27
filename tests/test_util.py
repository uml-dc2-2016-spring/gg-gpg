
import os
import stat
import sys
import unittest
import shutil

sys.path.insert(0, os.path.abspath('../lib'))
import util

class test_directory_manip(unittest.TestCase):

    def setUp(self):
        self.rootdir = '/tmp'
        self.dirname = 'test'

    def test_create_channel(self):
        cwd = os.getcwd()
        fifoname = 'in'
        logname = 'out'
        util.create_channel(self.dirname, self.rootdir, infile=fifoname, outfile=logname)

        # create_channel should return us to the working directory.
        self.assertEquals(cwd, os.getcwd(), 'create_channel() did not return caller to working directory.')

        os.chdir(os.path.join(self.rootdir, self.dirname))

        # stat.S_ISFIFO returns nonzero
        self.assertNotEqual(0, stat.S_ISFIFO(os.stat(fifoname).st_mode), 'create_channel did not produce a fifo file in channel directory with name %s' % fifoname)

        self.assertTrue(os.path.exists(logname), 'create_channel failed to produce a file named %s' % logname)

    def tearDown(self):
        shutil.rmtree(os.path.join(self.rootdir, self.dirname))

class test_process_manip(unittest.TestCase):

    def setUp(self):
        self.sed = 'sed \'s/asdf/gg/\' '
        self.echo = 'echo '
        self.testdata = 'asdfqwer'

    def test_get_output(self):
        """
            test that get_output returns successfully and executes as expected.
        """
        cmd = '%s %s' % (self.echo, self.testdata)
        actual = util.get_output(cmd)
        #echo replaces EOF with EOL
        expected = 'asdfqwer\n'

        self.assertEqual(expected, actual)

    def test_run_piped_proc(self):
        """
            test that run_piped_proc executes as expected
        """
        #run_piped_proc returns a tuple. [0] is stdout, [1] is stderr
        actual = util.run_piped_proc(self.sed, self.testdata)[0]
        expected = 'ggqwer'

        self.assertEqual(expected, actual)


class test_networking(unittest.TestCase):

    def test_resolve_hostname_google(self):
        """
            test just to confirm that this method does stuff. results cannot be guaranteed and compared.
        """
        util.resolve_hostname('www.google.com', 80)

    def test_resolve_hostname_localhost(self):
        actual = util.resolve_hostname('localhost', 9000)

        expected = [(2, 1, 6, '', ('127.0.0.1', 9000))]

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()

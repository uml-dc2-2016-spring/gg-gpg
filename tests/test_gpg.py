import sys
import os
import unittest
sys.path.insert(0, os.path.abspath('../lib'))

import gpg

class gpg_noclass_tests(unittest.TestCase):

    def setUp(self):
        self.testkey_id = '7713BCC79646AAF4'

    @unittest.skip('Not implemented yet.')
    def test_recv_keys(self):
        pass

    def test_get_public_ids(self):
        actual = gpg.get_public_ids()

        self.assertTrue(self.testkey_id in actual['keys'])

    def test_get_secret_ids(self):
        """
            this test will not work on other machines without the teskkeyID above.
        """
        actual = gpg.get_secret_ids()

        self.assertTrue(self.testkey_id in actual['keys'])

class gpg_instance_tests(unittest.TestCase):

    def setUp(self):
        self.testkey_id = '7713BCC79646AAF4'
        self.gpg = gpg.gpg([self.testkey_id])
        self.inputdata = 'asdf'

    def test_gpg_constructor_exception(self):
        with self.assertRaises(Exception):
            dummy = gpg.gpg([])

    def test_encrypt_cmd(self):
        expected = 'gpg --armor --recipient %s --encrypt ' % self.testkey_id
        self.assertEqual(expected, self.gpg.encrypt_cmd)

    def test_encrypt(self):
        expected = self.gpg.encrypt(self.inputdata)

if __name__ == '__main__':
    unittest.main()

import pkg_resources
import os.path

from unittest import TestCase

import pyeagle


data = pkg_resources.resource_filename('pyeagle.tests', 'data')


class TestOpen(TestCase):
    def test_open_lbr(self):
        lib = pyeagle.open(os.path.join(data, 'sample.lbr'))
        self.assertIn('SparkFun', lib.description)

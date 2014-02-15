import pkg_resources
import os.path

from unittest import TestCase

import pyeagle


data = pkg_resources.resource_filename('pyeagle.tests', 'data')


class TestSVGSmoke(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = pyeagle.open(os.path.join(data, 'sample.lbr'))

    def test_all_packages(self):
        for name, package in self.lib.packages.items():
            package.to_svg(scale=10, layers=self.lib.layers)

    def test_all_symbols(self):
        for name, symbol in self.lib.symbols.items():
            symbol.to_svg(scale=10, layers=self.lib.layers)

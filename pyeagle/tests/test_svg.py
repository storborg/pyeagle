import pkg_resources
import os.path

from unittest import TestCase

import pyeagle
from pyeagle.render import SVGRenderer


data = pkg_resources.resource_filename('pyeagle.tests', 'data')


class TestSVGSmoke(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = pyeagle.open(os.path.join(data, 'sample.lbr'))

    def test_all_packages(self):
        for name, package in self.lib.packages.items():
            SVGRenderer(package, self.lib.layers, scale=10).render_to_string()

    def test_all_symbols(self):
        for name, symbol in self.lib.symbols.items():
            SVGRenderer(symbol, self.lib.layers, scale=10).render_to_string()

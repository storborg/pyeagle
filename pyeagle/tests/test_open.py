import pkg_resources
import os.path

from unittest import TestCase

import pyeagle


data = pkg_resources.resource_filename('pyeagle.tests', 'data')


class TestOpenLibrary(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lib = pyeagle.open(os.path.join(data, 'sample.lbr'))

    def test_description(self):
        self.assertIn('SparkFun', self.lib.description)

    def test_device_sets(self):
        device_sets = self.lib.device_sets
        self.assertEqual(len(device_sets), 91)

    def test_device_set(self):
        device_set = self.lib.device_sets['GEIGER_TUBE']
        self.assertIn('LND712', device_set.description)
        self.assertEqual(device_set.prefix, 'U')

    def test_symbols(self):
        symbols = self.lib.symbols
        self.assertEqual(len(symbols), 94)

    def test_symbol(self):
        symbol = self.lib.symbols['GEIGER_TUBE']
        self.assertEqual(len(symbol.pins), 2)

    def test_packages(self):
        packages = self.lib.packages
        self.assertEqual(len(packages), 99)

    def test_package(self):
        package = self.lib.packages['GEIGER_TUBE']
        self.assertEqual(len(package.pads), 2)


class TestOpenSchematic(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schematic = pyeagle.open(os.path.join(data, 'sample.sch'))

    def test_libraries(self):
        libraries = self.schematic.libraries
        self.assertEqual(len(libraries), 18)


class TestOpenBoard(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.board = pyeagle.open(os.path.join(data, 'sample.brd'))

    def test_libraries(self):
        libraries = self.board.libraries
        # Note the board has one less library because the supply lib is used in
        # the schematic but not the board.
        self.assertEqual(len(libraries), 17)


class TestOpenBad(TestCase):
    def test_valid_xml(self):
        with self.assertRaises(NotImplementedError):
            pyeagle.open(os.path.join(data, 'valid-xml-but-bad-file.xml'))

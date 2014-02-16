import pkg_resources
import os.path

from unittest import TestCase

import pyeagle


data = pkg_resources.resource_filename('pyeagle.tests', 'data')


class DrawingMixin(object):

    def test_settings(self):
        settings = self.obj.settings
        self.assertTrue(isinstance(settings, dict))

    def test_grid(self):
        grid = self.obj.grid
        self.assertEqual(grid['style'], 'lines')

    def test_layers(self):
        layers = self.obj.layers
        layers.is_visible(1)


class TestOpenLibrary(TestCase, DrawingMixin):
    @classmethod
    def setUpClass(cls):
        cls.lib = cls.obj = pyeagle.open(os.path.join(data, 'sample.lbr'))

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


class TestOpenSchematic(TestCase, DrawingMixin):
    @classmethod
    def setUpClass(cls):
        cls.schematic = cls.obj = \
            pyeagle.open(os.path.join(data, 'sample.sch'))

    def test_libraries(self):
        libraries = self.schematic.libraries
        self.assertEqual(len(libraries), 18)

    def test_classes(self):
        classes = self.schematic.classes
        self.assertEqual(len(classes), 1)
        cls = classes[0]
        self.assertEqual(cls.number, 0)
        self.assertEqual(cls.width, 0.1524)
        self.assertEqual(cls.name, 'default')
        self.assertEqual(cls.drill, 0.3048)

    def test_sheets(self):
        sheets = self.schematic.sheets
        self.assertEqual(len(sheets), 1)

    def test_sheet_nets(self):
        sheet = self.schematic.sheets[0]
        nets = sheet.nets
        self.assertEqual(len(nets), 107)

        ground_net = nets['GND']
        segments = ground_net.segments
        self.assertEqual(len(segments), 30)

    def test_sheet_instances(self):
        sheet = self.schematic.sheets[0]
        instances = sheet.instances
        self.assertEqual(len(instances), 132)


class TestOpenBoard(TestCase, DrawingMixin):
    @classmethod
    def setUpClass(cls):
        cls.board = cls.obj = pyeagle.open(os.path.join(data, 'sample.brd'))

    def test_libraries(self):
        libraries = self.board.libraries
        # Note the board has one less library because the 'supply' lib is used
        # in the schematic but not the board.
        self.assertEqual(len(libraries), 17)


class TestOpenBad(TestCase):
    def test_valid_xml(self):
        with self.assertRaises(NotImplementedError):
            pyeagle.open(os.path.join(data, 'valid-xml-but-bad-file.xml'))

"""
PyEAGLE types: different objects represented in CAD files.
"""
from collections import OrderedDict

from .geometry import Geometry, Pin, Pad, SMD


class Package(Geometry):
    """
    Represents a package (aka footprint) of an EAGLE part.
    """
    def __init__(self, name, primitives=None):
        Geometry.__init__(self, primitives)
        self.name = name

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    @property
    def pads(self):
        return [prim for prim in self.primitives
                if isinstance(prim, (Pad, SMD))]

    @classmethod
    def from_xml(cls, package_root):
        name = package_root.attrib['name']
        primitives = cls.geometry_from_xml(package_root)
        return cls(name=name, primitives=primitives)


class Symbol(Geometry):
    """
    Represents a symbol in an EAGLE schematic or library.
    """
    def __init__(self, name, primitives=None):
        Geometry.__init__(self, primitives)
        self.name = name

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    @property
    def pins(self):
        return [prim for prim in self.primitives
                if isinstance(prim, Pin)]

    @classmethod
    def from_xml(cls, symbol_root):
        name = symbol_root.attrib['name']
        primitives = cls.geometry_from_xml(symbol_root)
        return cls(name=name, primitives=primitives)


class Gate(object):
    """
    Represents a gate in a schematic / library device set.
    """
    def __init__(self, name, symbol, x, y):
        self.name = name
        self.symbol = symbol
        self.x = x
        self.y = y

    @classmethod
    def from_xml(cls, gate_node):
        # FIXME Resolve reference
        symbol = None
        return cls(name=gate_node.attrib['name'],
                   symbol=symbol,
                   x=gate_node.attrib['x'],
                   y=gate_node.attrib['y'])


class DeviceSet(object):
    """
    Represents a device set (in a library).
    """
    def __init__(self, name, prefix=None, gates=None, uservalue=False,
                 description=u''):
        self.name = name
        self.prefix = prefix
        self.gates = gates or []
        self.uservalue = uservalue
        self.description = description

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    @classmethod
    def from_xml(cls, ds_root):
        name = ds_root.attrib['name']
        prefix = ds_root.attrib.get('prefix')
        uservalue = ds_root.attrib.get('uservalue') == 'yes'

        desc_nodes = ds_root.xpath('description')
        if desc_nodes:
            description = desc_nodes[0].text
        else:
            description = u''

        gates = []
        for gate_node in ds_root.xpath('gates/gate'):
            gates.append(Gate.from_xml(gate_node))

        return cls(name=name, prefix=prefix, uservalue=uservalue,
                   description=description, gates=gates)


class Device(object):
    """
    Represents a device in an EAGLE schematic, PCB, or library.
    """
    def __init__(self, package, name):
        self.name = name
        self.package = package

    def __repr__(self):
        return '<%s %r package:%r>' % (self.__class__.__name__, self.name,
                                       self.package.name)


class Library(object):
    """
    Represents an EAGLE parts library.
    """
    def __init__(self, name=None, description=None,
                 packages=None, symbols=None, device_sets=None,
                 from_file=None):
        self.name = name
        self.description = description
        self.packages = packages or OrderedDict()
        self.symbols = symbols or OrderedDict()
        self.device_sets = device_sets or OrderedDict()
        self.from_file = from_file

    def __repr__(self):
        from_file = self.from_file or 'unknown'
        return '<%s %r>' % (self.__class__.__name__, from_file)

    @classmethod
    def from_xml(cls, lib_root, from_file=None):
        name = lib_root.attrib.get('name')

        # FIXME this xpath selector may have an issue, it should really only
        # select from a description tag which is an immediate child of the root
        # node.
        desc_nodes = lib_root.xpath('description')
        if desc_nodes:
            description = desc_nodes[0].text
        else:
            description = None

        packages = OrderedDict()
        for package_node in lib_root.xpath('packages/package'):
            package = Package.from_xml(package_node)
            packages[package.name] = package

        symbols = OrderedDict()
        for symbol_node in lib_root.xpath('symbols/symbol'):
            symbol = Symbol.from_xml(symbol_node)
            symbols[symbol.name] = symbol

        device_sets = OrderedDict()
        for ds_node in lib_root.xpath('devicesets/deviceset'):
            device_set = DeviceSet.from_xml(ds_node)
            device_sets[device_set.name] = device_set

        return cls(name=name,
                   description=description, packages=packages, symbols=symbols,
                   device_sets=device_sets, from_file=from_file)

    def __iter__(self):
        return iter(self.device_sets)


class Part(object):
    """
    A part in a schematic sheet.
    """


class Sheet(Geometry):
    """
    A sheet in a schematic.
    """
    def __init__(self):
        self.instances = []
        self.nets = []
        self.busses = []


class Schematic(object):
    """
    Represents an EAGLE schematic.
    """
    def __init__(self, libraries=None):
        self.classes = []
        self.libraries = libraries or OrderedDict()
        self.parts = OrderedDict()
        self.sheets = []

    @classmethod
    def from_xml(cls, node, from_file=None):
        libraries = OrderedDict()
        for lib_node in node.xpath('libraries/library'):
            lib = Library.from_xml(lib_node)
            libraries[lib.name] = lib

        return cls(
            libraries=libraries,
        )


class AutorouterRules(object):
    pass


class DesignRules(object):
    """
    A set of PCB design rules.
    """
    def __init__(self, descriptions=None, params=None):
        self.descriptions = descriptions or {}
        self.params = params or {}

    @classmethod
    def from_xml(cls, node):
        descriptions = {}
        for desc_node in node.xpath('description'):
            lang = desc_node.attrib['language']
            descriptions[lang] = desc_node.text

        params = {}
        for param_node in node.xpath('param'):
            params[param_node.attrib['name']] = param_node.attrib['value']

        return cls(descriptions=descriptions,
                   params=params)


class Signal(Geometry):
    """
    A signal in a board.
    """


class Board(Geometry):
    """
    An EAGLE printed circuit board layout.
    """
    def __init__(self, libraries=None):
        self.libraries = libraries or OrderedDict()

    @classmethod
    def from_xml(cls, node, from_file=None):
        libraries = OrderedDict()
        for lib_node in node.xpath('libraries/library'):
            lib = Library.from_xml(lib_node)
            libraries[lib.name] = lib

        return cls(
            libraries=libraries,
        )

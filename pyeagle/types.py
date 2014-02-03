"""
PyEAGLE types: different objects represented in CAD files.
"""

from .geometry import Geometry


class Package(Geometry):
    """
    Represents a package (aka footprint) of an EAGLE part.
    """
    def __init__(self, name, primitives=None):
        Geometry.__init__(self, primitives)
        self.name = name

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

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
    def __init__(self, description=u'',
                 packages=None, symbols=None, device_sets=None,
                 from_file=None):
        self.description = description
        self.packages = packages or []
        self.symbols = symbols or []
        self.device_sets = device_sets or []
        self.from_file = from_file

    def __repr__(self):
        from_file = self.from_file or 'unknown'
        return '<%s %r>' % (self.__class__.__name__, from_file)

    @classmethod
    def from_xml(cls, lib_root, from_file=None):
        # FIXME this xpath selector may have an issue, it should really only
        # select from a description tag which is an immediate child of the root
        # node.
        desc_node = lib_root.xpath('description')[0]
        description = desc_node.text

        packages = []
        for package_node in lib_root.xpath('packages/package'):
            packages.append(Package.from_xml(package_node))

        symbols = []
        for symbol_node in lib_root.xpath('symbols/symbol'):
            symbols.append(Symbol.from_xml(symbol_node))

        device_sets = []
        for ds_node in lib_root.xpath('devicesets/deviceset'):
            device_sets.append(DeviceSet.from_xml(ds_node))

        return cls(description=description, packages=packages, symbols=symbols,
                   device_sets=device_sets, from_file=from_file)

    def __iter__(self):
        return iter(self.device_sets)

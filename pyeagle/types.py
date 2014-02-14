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
        """
        Enumerate the pads (SMD and through-hole) on this package.
        """
        return [prim for prim in self.primitives
                if isinstance(prim, (Pad, SMD))]

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Package from a ``<package>`` XML node in EAGLE's XML
        format.
        """
        name = node.attrib['name']
        primitives = cls.geometry_from_xml(node)
        return cls(name=name, primitives=primitives)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


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
        """
        Enumerate the pins on this symbol.
        """
        return [prim for prim in self.primitives
                if isinstance(prim, Pin)]

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Symbol from a ``<symbol>`` XML node in EAGLE's XML format.
        """
        name = node.attrib['name']
        primitives = cls.geometry_from_xml(node)
        return cls(name=name, primitives=primitives)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


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
        """
        Construct a Gate from a ``<gate>`` XML node in EAGLE's XML format.
        """
        # FIXME Resolve reference
        symbol = None
        return cls(name=gate_node.attrib['name'],
                   symbol=symbol,
                   x=gate_node.attrib['x'],
                   y=gate_node.attrib['y'])

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class DeviceSet(object):
    """
    Represents a device set (in a library).
    """
    def __init__(self, name, prefix=None,
                 gates=None, devices=None,
                 uservalue=False, description=u''):
        self.name = name
        self.prefix = prefix
        self.gates = gates or OrderedDict()
        self.devices = devices or OrderedDict()
        self.uservalue = uservalue
        self.description = description

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.name)

    @classmethod
    def from_xml(cls, node):
        """
        Construct a DeviceSet from a ``<deviceset>`` XML node in EAGLE's XML
        format.
        """
        name = node.attrib['name']
        prefix = node.attrib.get('prefix')
        uservalue = node.attrib.get('uservalue') == 'yes'

        desc_nodes = node.xpath('description')
        if desc_nodes:
            description = desc_nodes[0].text
        else:
            description = u''

        gates = OrderedDict()
        for gate_node in node.xpath('gates/gate'):
            gate = Gate.from_xml(gate_node)
            gates[gate.name] = gate

        devices = OrderedDict()
        for d_node in node.xpath('devices/device'):
            device = Device.from_xml(d_node)
            devices[device.name] = device

        return cls(name=name, prefix=prefix, uservalue=uservalue,
                   description=description, gates=gates, devices=devices)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class Device(object):
    """
    Represents a device in an EAGLE schematic, PCB, or library.

    FIXME Add pin connections and technologies
    """
    def __init__(self, package, name):
        self.name = name
        self.package = package

    def __repr__(self):
        return '<%s %r package:%r>' % (self.__class__.__name__, self.name,
                                       self.package.name)

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Device from a ``<device>`` node in EAGLE's XML format.
        """
        name = node.attrib['name']
        return cls(
            name=name,
            package=None,
        )

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def __iter__(self):
        return iter(self.device_sets)

    def save(self, f):
        """
        Save this library to a file.

        :param f:
            Filename or file-like object.
        """
        raise NotImplementedError


class Part(object):
    """
    A part in a schematic sheet.
    """
    def __init__(self, name, device, value=None):
        self.name = name
        self.device = device
        self.value = value

    @classmethod
    def from_xml(cls, node, libraries):
        name = node.attrib['name']
        value = node.attrib.get('value')

        lib_name = node.attrib['library']
        ds_name = node.attrib['deviceset']
        d_name = node.attrib['device']

        lib = libraries[lib_name]
        ds = lib.device_sets[ds_name]
        device = ds.devices[d_name]

        return cls(name=name, device=device, value=value)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class Sheet(Geometry):
    """
    A sheet in a schematic.
    """
    def __init__(self):
        self.instances = []
        self.nets = []
        self.busses = []

    @classmethod
    def from_xml(cls, node):
        return cls(
        )

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def to_svg(self, scale):
        """
        Render this schematiic sheet as an SVG.
        """
        raise NotImplementedError


class Schematic(object):
    """
    Represents an EAGLE schematic.
    """
    def __init__(self, libraries=None, parts=None):
        self.classes = []
        self.libraries = libraries or OrderedDict()
        self.parts = parts or OrderedDict()
        self.sheets = []

    @classmethod
    def from_xml(cls, node, from_file=None):
        libraries = OrderedDict()
        for lib_node in node.xpath('libraries/library'):
            lib = Library.from_xml(lib_node)
            libraries[lib.name] = lib

        parts = OrderedDict()
        for part_node in node.xpath('parts/part'):
            part = Part.from_xml(part_node, libraries)
            parts[part.name] = part

        return cls(
            libraries=libraries,
            parts=parts,
        )

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def save(self, f):
        """
        Save this schematic to a file.

        :param f:
            Filename or file-like object.
        """
        raise NotImplementedError


class AutorouterPass(object):
    """
    A single autorouter pass.
    """
    def __init__(self, params=None):
        self.params = params or {}

    @classmethod
    def from_xml(cls, node):
        params = {}
        for param_node in node.xpath('param'):
            params[param_node.attrib['name']] = param_node.attrib['value']
        return cls(params=params)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class AutorouterRules(object):
    """
    A set of autorouter control parameters.
    """
    def __init__(self, passes=None):
        self.passes = passes or []

    @classmethod
    def from_xml(cls, node):
        passes = []
        for pass_node in node.xpath('pass'):
            passes.append(AutorouterPass.from_xml(pass_node))
        return cls(passes=passes)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def save(self, f):
        """
        Save this set of autorouter rules to a file.

        :param f:
            Filename or file-like object.
        """
        raise NotImplementedError


class DesignRules(object):
    """
    A set of PCB design rules.
    """
    def __init__(self, name=None, descriptions=None, params=None):
        self.name = name
        self.descriptions = descriptions or {}
        self.params = params or {}

    @classmethod
    def from_xml(cls, node):
        name = node.attrib.get('name')

        descriptions = {}
        for desc_node in node.xpath('description'):
            lang = desc_node.attrib['language']
            descriptions[lang] = desc_node.text

        params = {}
        for param_node in node.xpath('param'):
            params[param_node.attrib['name']] = param_node.attrib['value']

        return cls(name=name,
                   descriptions=descriptions,
                   params=params)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def save(self, f):
        """
        Save this set of design rules to a file.

        :param f:
            Filename or file-like object.
        """
        raise NotImplementedError


class Bus(Geometry):
    """
    A bus in a schematic. Basically a multichannel Net.
    """
    def __init__(self):
        pass

    @classmethod
    def from_xml(cls, node):
        return cls()

    def to_xml(self):
        raise NotImplementedError


class Net(Geometry):
    """
    A net in a schematic. The same thing in a board is a called a Signal.

    FIXME Maybe a segment should be a class which inherits from Geometry.
    """
    def __init__(self, name, class_, segments=None):
        self.name = name
        self.class_ = class_
        self.segments = segments or []

    @classmethod
    def from_xml(cls, node):
        return cls()

    def to_xml(self):
        raise NotImplementedError


class Signal(Geometry):
    """
    A signal in a board. The same thing in a schematic is called a Net.
    """
    def __init__(self, name, contacts):
        pass

    @classmethod
    def from_xml(cls, node):
        return cls()

    def to_xml(self):
        raise NotImplementedError


class Board(Geometry):
    """
    An EAGLE printed circuit board layout.
    """
    def __init__(self, libraries=None, design_rules=None,
                 autorouter_rules=None):
        self.libraries = libraries or OrderedDict()
        self.design_rules = design_rules
        self.autorouter_rules = autorouter_rules

    @classmethod
    def from_xml(cls, node, from_file=None):
        libraries = OrderedDict()
        for lib_node in node.xpath('libraries/library'):
            lib = Library.from_xml(lib_node)
            libraries[lib.name] = lib

        design_rules_node = node.xpath('designrules')[0]
        design_rules = DesignRules.from_xml(design_rules_node)

        autorouter_rules_node = node.xpath('autorouter')[0]
        autorouter_rules = AutorouterRules.from_xml(autorouter_rules_node)

        return cls(
            libraries=libraries,
            design_rules=design_rules,
            autorouter_rules=autorouter_rules,
        )

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def save(self, f):
        """
        Save this board to a file.

        :param f:
            Filename or file-like object.
        """
        raise NotImplementedError

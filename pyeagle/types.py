"""
PyEAGLE types: different objects represented in CAD files.
"""
from collections import OrderedDict

from .geometry import Geometry, Pin, Pad, SMD
from .layers import LayerSet


def settings_from_xml(node):
    settings = {}
    for setting_node in node.xpath('setting'):
        settings.update(node.attrib)
    return settings


def grid_from_xml(node):
    return node.attrib


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
    def from_xml(cls, node, packages):
        """
        Construct a DeviceSet from a ``<deviceset>`` XML node in EAGLE's XML
        format.
        """
        name = node.attrib['name']
        prefix = node.attrib.get('prefix')
        uservalue = node.attrib.get('uservalue') == 'yes'

        desc_nodes = node.xpath('.//description')
        if desc_nodes:
            description = desc_nodes[0].text
        else:
            description = u''

        gates = OrderedDict()
        for gate_node in node.xpath('.//gates/gate'):
            gate = Gate.from_xml(gate_node)
            gates[gate.name] = gate

        devices = OrderedDict()
        for d_node in node.xpath('.//devices/device'):
            device = Device.from_xml(d_node, packages)
            devices[device.name] = device

        return cls(name=name, prefix=prefix, uservalue=uservalue,
                   description=description, gates=gates, devices=devices)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class Attribute(object):
    def __init__(self, name, value, constant=None):
        self.name = name
        self.value = value
        self.constant = constant

    def __repr__(self):
        return '<%s %r:%r>' % (self.__class__.__name__,
                               self.name,
                               self.value)

    def as_dict(self):
        return {self.name: self.value}

    @classmethod
    def from_xml(cls, node):
        return cls(
            name=node.attrib['name'],
            value=node.attrib['value'],
            constant=(node.attrib['constant']
                      if 'constant' in node.attrib.keys()
                      else None)
        )


class Technology(object):
    def __init__(self, name, attributes):
        self.name = name
        self.attributes = attributes

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__,
                            self.attributes)

    def as_dict(self):
        return {d.name: d.value for d in self.attributes}

    @classmethod
    def from_xml(cls, node):
        return cls(
            name=node.attrib['name'],
            attributes=[Attribute.from_xml(n) for n in
                        node.xpath('.//attribute')]
        )


class Device(object):
    """
    Represents a device in an EAGLE schematic, PCB, or library.

    FIXME Add pin connections
    """
    def __init__(self, package, name, technologies):
        self.name = name
        self.package = package
        self.technologies = technologies

    def __repr__(self):
        return '<%s %r package:%r>' % (self.__class__.__name__,
                                       self.name if self.name else '',
                                       self.package.name)

    @classmethod
    def from_xml(cls, node, packages):
        """
        Construct a Device from a ``<device>`` node in EAGLE's XML format.
        """
        name = node.attrib['name']
        try:
            package = packages[node.attrib['package']]
        except KeyError:
            package = Package(name='')

        technologies = [Technology.from_xml(n) for n in
                        node.xpath('.//technologies/technology')]
        technologies = {t.name: t for t in technologies}

        return cls(
            name=name,
            package=package,
            technologies=technologies
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
                 from_file=None, layers=None, grid=None, settings=None):
        self.name = name
        self.description = description
        self.packages = packages or OrderedDict()
        self.symbols = symbols or OrderedDict()
        self.device_sets = device_sets or OrderedDict()
        self.from_file = from_file
        self.layers = layers
        self.settings = settings
        self.grid = grid

    def __repr__(self):
        from_file = self.from_file or 'unknown'
        return '<%s %r>' % (self.__class__.__name__, from_file)

    @classmethod
    def from_xml(cls, lib_root, layers, settings, grid, from_file=None):
        """
        Construct a Library from a ``<library>`` node in EAGLE's XML format.
        """
        name = lib_root.attrib.get('name')

        desc_nodes = lib_root.xpath('.//description')
        if desc_nodes:
            description = desc_nodes[0].text
        else:
            description = None

        packages = OrderedDict()
        for package_node in lib_root.xpath('.//packages/package'):
            package = Package.from_xml(package_node)
            packages[package.name] = package

        symbols = OrderedDict()
        for symbol_node in lib_root.xpath('.//symbols/symbol'):
            symbol = Symbol.from_xml(symbol_node)
            symbols[symbol.name] = symbol

        device_sets = OrderedDict()
        for ds_node in lib_root.xpath('.//devicesets/deviceset'):
            device_set = DeviceSet.from_xml(ds_node, packages)
            device_sets[device_set.name] = device_set

        return cls(name=name,
                   description=description,
                   packages=packages,
                   symbols=symbols,
                   device_sets=device_sets,
                   from_file=from_file,
                   layers=layers,
                   settings=settings,
                   grid=grid)

    @classmethod
    def from_drawing_xml(cls, node, from_file=None):
        """
        Construct a Library from a ``<drawing>`` node in EAGLE's XML format.
        """
        layer_nodes = node.xpath('layers')
        layers = LayerSet.from_xml(layer_nodes[0])

        settings_node = node.xpath('settings')[0]
        settings = settings_from_xml(settings_node)

        grid_node = node.xpath('grid')[0]
        grid = grid_from_xml(grid_node)

        lib_root = node.xpath('library')[0]
        return cls.from_xml(lib_root,
                            layers=layers,
                            grid=grid,
                            settings=settings,
                            from_file=from_file)

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
    def __init__(self, name, device, device_set=None, value=None,
                 technology=None, attributes=dict()):
        self.name = name
        self.device = device
        self.device_set = device_set
        self.value = value
        self.technology = technology
        self.attributes = attributes

    @classmethod
    def from_xml(cls, node, libraries):
        """
        Construct a Part from a ``<part>`` node in EAGLE's XML format.
        """
        name = node.attrib['name']
        value = node.attrib.get('value')

        lib_name = node.attrib['library']
        ds_name = node.attrib['deviceset']
        d_name = node.attrib['device']
        technology_name = (node.attrib['technology']
                           if 'technology' in node.attrib.keys() else '')

        lib = libraries[lib_name]
        ds = lib.device_sets[ds_name]
        device = ds.devices[d_name]

        attributes = OrderedDict()
        for attribute_node in node.xpath('.//attribute'):
            attributes[attribute_node.attrib['name']] = \
                attribute_node.attrib['value']

        return cls(name=name,
                   device=device,
                   device_set=ds,
                   value=value,
                   technology=technology_name,
                   attributes=attributes)

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class Instance(object):
    """
    A gate instance of a part in a schematic sheet.
    """
    def __init__(self, part, gate, pos, smashed=False, mirrored=False,
                 rotate=0):
        self.part = part
        self.gate = gate
        self.x, self.y = pos
        self.smashed = smashed
        self.mirrored = mirrored
        self.rotate = rotate

    @classmethod
    def from_xml(cls, node):
        """
        Construct an Instance from a ``<instance>`` node in EAGLE's XML format.
        """
        part = node.attrib['part']
        gate = node.attrib['gate']
        x = float(node.attrib['x'])
        y = float(node.attrib['y'])

        smashed = (node.attrib.get('smashed') == 'yes')
        rot = node.attrib.get('rot', 'R0')
        if rot.startswith('M'):
            mirrored = True
            rotate = int(rot[2:])
        else:
            mirrored = False
            rotate = int(rot[1:])

        return cls(
            part=part,
            gate=gate,
            pos=(x, y),
            smashed=smashed,
            mirrored=mirrored,
            rotate=rotate,
        )

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class Sheet(Geometry):
    """
    A sheet in a schematic.

    A sheet has:
        - plain elements (drawing primitives)
        - instances
        - busses
        - nets
    """
    def __init__(self, primitives=None, instances=None, nets=None,
                 busses=None):
        Geometry.__init__(self, primitives)
        self.instances = instances or {}
        self.nets = nets or {}
        self.busses = busses or {}

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Sheet from a ``<sheet>`` node in EAGLE's XML format.
        """
        instances = {}
        for instance_node in node.xpath('instances/instance'):
            instance = Instance.from_xml(instance_node)
            instances[(instance.part, instance.gate)] = instance

        nets = {}
        for net_node in node.xpath('nets/net'):
            net = Net.from_xml(net_node)
            nets[net.name] = net

        busses = {}
        for bus_node in node.xpath('busses/bus'):
            bus = Bus.from_xml(bus_node)
            busses[bus.name] = bus

        primitives = cls.geometry_from_xml(node)
        return cls(
            primitives=primitives,
            instances=instances,
            busses=busses,
            nets=nets,
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


class SignalClass(object):
    """
    Represents an EAGLE signal class: e.g. one might have classes for
    "default", "analog", and "power".
    """
    def __init__(self, number, name, width, drill, clearance):
        self.number = number
        self.name = name
        self.width = width
        self.drill = drill
        self.clearance = clearance

    @classmethod
    def from_xml(cls, node):
        number = int(node.attrib['number'])
        name = node.attrib['name']
        width = float(node.attrib['width'])
        drill = float(node.attrib['drill'])

        clearance_node = node.xpath('clearance')
        if len(clearance_node) != 0:
            clearance = float(clearance_node[0].attrib['value'])
        else:
            clearance = None

        return cls(
            number=number,
            name=name,
            width=width,
            drill=drill,
            clearance=clearance,
        )


class Schematic(object):
    """
    Represents an EAGLE schematic.
    """
    def __init__(self, classes=None, sheets=None, libraries=None, parts=None,
                 layers=None, settings=None, grid=None):
        self.classes = classes or {}
        self.libraries = libraries or OrderedDict()
        self.parts = parts or OrderedDict()
        self.sheets = sheets or []
        self.layers = layers
        self.settings = settings
        self.grid = grid

    @classmethod
    def from_drawing_xml(cls, node, from_file=None):
        """
        Construct a Schematic from a ``<drawing>`` node in EAGLE's XML format.
        """
        layer_nodes = node.xpath('layers')
        layers = LayerSet.from_xml(layer_nodes[0])

        settings_node = node.xpath('settings')[0]
        settings = settings_from_xml(settings_node)

        grid_node = node.xpath('grid')[0]
        grid = grid_from_xml(grid_node)

        schem_root = node.xpath('schematic')[0]

        classes = {}
        for class_node in schem_root.xpath('classes/class'):
            signal_class = SignalClass.from_xml(class_node)
            classes[signal_class.number] = signal_class

        libraries = OrderedDict()
        for lib_node in schem_root.xpath('libraries/library'):
            lib = Library.from_xml(lib_node, layers=layers, settings=settings,
                                   grid=grid)
            libraries[lib.name] = lib

        parts = OrderedDict()
        for part_node in schem_root.xpath('parts/part'):
            part = Part.from_xml(part_node, libraries)
            parts[part.name] = part

        sheets = []
        for sheet_node in schem_root.xpath('sheets/sheet'):
            sheets.append(Sheet.from_xml(sheet_node))

        return cls(
            classes=classes,
            libraries=libraries,
            parts=parts,
            sheets=sheets,
            layers=layers,
            settings=settings,
            grid=grid,
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


class AutorouterRules(object):
    """
    A set of autorouter control parameters. Has a list of passes, each of whih
    is a dict of parameters.
    """
    def __init__(self, passes=None):
        self.passes = passes or []

    @classmethod
    def from_xml(cls, node):
        """
        Construct an AutorouterRules instance from an EAGLE XML
        ``<autorouter>`` node.
        """
        passes = []
        for pass_node in node.xpath('pass'):
            params = {}
            for param_node in pass_node.xpath('param'):
                params[param_node.attrib['name']] = param_node.attrib['value']
            passes.append(params)
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
        """
        Construct a DesignRules instance from an EAGLE XML ``<designrules>``
        node.
        """
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
    def __init__(self, name, primitives=None, segments=None):
        super(Bus, self).__init__(primitives=primitives)
        self.name = name
        self.segments = segments

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Bus from an EAGLE XML ``<bus>`` node.
        """
        primitives = cls.geometry_from_xml(node)

        segments = []
        for segment_node in node.xpath('.//segment'):
            segment = Segment.from_xml(segment_node)
            segments.append(segment)

        return cls(name=node.attrib['name'],
                   primitives=primitives,
                   segments=segments)

    def to_xml(self):
        """
        Serialize this to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class Segment(Geometry):
    """
    A segment in a net.
    """
    def __init__(self, pins=None, junctions=None, primitives=None):
        Geometry.__init__(self, primitives=primitives)
        self.pins = pins or []
        self.junctions = junctions or []

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Segment from an EAGLE XML ``<segment>`` node.
        """
        primitives = cls.geometry_from_xml(node)

        pins = []
        for pin_node in node.xpath('pinref'):
            pass

        junctions = []
        for junction_node in node.xpath('junction'):
            junctions.append((junction_node.attrib['x'],
                              junction_node.attrib['y']))

        return cls(primitives=primitives,
                   pins=pins,
                   junctions=junctions)


class Net(object):
    """
    A net in a schematic. The same thing in a board is a called a Signal.
    """
    def __init__(self, name, class_, segments=None):
        self.name = name
        self.class_ = class_
        self.segments = segments or []

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Net from an EAGLE XML ``<net>`` node.
        """
        name = node.attrib['name']
        class_ = node.attrib['class']

        segments = []
        for segment_node in node.xpath('.//segment'):
            segment = Segment.from_xml(segment_node)
            segments.append(segment)

        return cls(name=name,
                   class_=class_,
                   segments=segments)

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
        """
        Construct a Signal from an EAGLE XML ``<signal>`` node.
        """
        return cls()

    def to_xml(self):
        """
        Serialize this to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError


class Board(Geometry):
    """
    An EAGLE printed circuit board layout.
    """
    def __init__(self, libraries=None, design_rules=None,
                 autorouter_rules=None, layers=None, settings=None, grid=None):
        self.libraries = libraries or OrderedDict()
        self.design_rules = design_rules
        self.autorouter_rules = autorouter_rules
        self.layers = layers
        self.settings = settings
        self.grid = grid

    @classmethod
    def from_drawing_xml(cls, node, from_file=None):
        """
        Construct a Board from an EAGLE XML ``<drawing>`` node.
        """
        layer_nodes = node.xpath('layers')
        layers = LayerSet.from_xml(layer_nodes[0])

        settings_node = node.xpath('settings')[0]
        settings = settings_from_xml(settings_node)

        grid_node = node.xpath('grid')[0]
        grid = grid_from_xml(grid_node)

        board_root = node.xpath('board')[0]

        libraries = OrderedDict()
        for lib_node in board_root.xpath('libraries/library'):
            lib = Library.from_xml(lib_node, layers=layers, settings=settings,
                                   grid=grid)
            libraries[lib.name] = lib

        design_rules_node = board_root.xpath('designrules')[0]
        design_rules = DesignRules.from_xml(design_rules_node)

        autorouter_rules_node = board_root.xpath('autorouter')[0]
        autorouter_rules = AutorouterRules.from_xml(autorouter_rules_node)

        return cls(
            libraries=libraries,
            design_rules=design_rules,
            autorouter_rules=autorouter_rules,
            layers=layers,
            settings=settings,
            grid=grid,
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

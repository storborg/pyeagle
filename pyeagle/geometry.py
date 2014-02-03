class Wire(object):
    def __init__(self, start, end, width, layer, curve=None, cap=None):
        self.x1, self.y1 = start
        self.x2, self.y2 = end
        self.width = width
        self.layer = layer
        self.curve = curve
        self.cap = cap

    def __repr__(self):
        return '<%s (%f, %f) -> (%f, %f)>' % (self.__class__.__name__,
                                              self.x1, self.y1,
                                              self.x2, self.y2)

    @classmethod
    def from_xml(cls, node):
        curve = node.attrib.get('curve')
        curve = curve and float(curve)
        return cls(start=(float(node.attrib['x1']),
                          float(node.attrib['y1'])),
                   end=(float(node.attrib['x2']),
                        float(node.attrib['y2'])),
                   width=float(node.attrib['width']),
                   layer=int(node.attrib['layer']),
                   curve=curve,
                   cap=node.attrib.get('cap'))


class SMD(object):
    def __init__(self, name, pos, size, layer):
        self.name = name
        self.x, self.y = pos
        self.dx, self.dy = size
        self.layer = layer

    def __repr__(self):
        return '<%s %r (%f, %f)>' % (self.__class__.__name__,
                                     self.name,
                                     self.x, self.y)

    @classmethod
    def from_xml(cls, node):
        return cls(name=node.attrib['name'],
                   pos=(float(node.attrib['x']),
                        float(node.attrib['y'])),
                   size=(float(node.attrib['dx']),
                         float(node.attrib['dy'])),
                   layer=int(node.attrib['layer']))


class Text(object):
    def __init__(self, s, pos, size, layer, ratio=None):
        self.s = s
        self.x, self.y = pos
        self.size = size
        self.layer = layer
        self.ratio = ratio

    def __repr__(self):
        return '<%s %r (%f, %f)>' % (self.__class__.__name__,
                                     self.s,
                                     self.x, self.y)

    @classmethod
    def from_xml(cls, node):
        ratio = node.attrib.get('ratio')
        ratio = ratio and float(ratio)
        return cls(s=node.text,
                   pos=(float(node.attrib['x']),
                        float(node.attrib['y'])),
                   size=float(node.attrib['size']),
                   layer=int(node.attrib['layer']),
                   ratio=ratio)


class Rectangle(object):
    def __init__(self, start, end, layer):
        self.x1, self.y1 = start
        self.x2, self.y2 = end
        self.layer = layer

    def __repr__(self):
        return '<%s (%f, %f) -> (%f, %f)>' % (self.__class__.__name__,
                                              self.x1, self.y1,
                                              self.x2, self.y2)

    @classmethod
    def from_xml(cls, node):
        return cls(start=(float(node.attrib['x1']),
                          float(node.attrib['y1'])),
                   end=(float(node.attrib['x2']),
                        float(node.attrib['y2'])),
                   layer=int(node.attrib['layer']))


class Pad(object):
    def __init__(self, name, pos, drill, diameter):
        self.name = name
        self.x, self.y = pos
        self.drill = drill
        self.diameter = diameter

    def __repr__(self):
        return '<%s (%f, %f) %f>' % (self.__class__.__name__,
                                     self.x, self.y,
                                     self.diameter)

    @classmethod
    def from_xml(cls, node):
        return cls(name=node.attrib['name'],
                   pos=(float(node.attrib['x']),
                        float(node.attrib['y'])),
                   drill=float(node.attrib['drill']),
                   diameter=float(node.attrib.get('diameter', 0)))


class Pin(object):
    def __init__(self, name, pos, length, direction, rotate, visible=False):
        self.name = name
        self.x, self.y = pos
        self.visible = visible
        self.length = length
        self.direction = direction
        self.rotate = rotate

    def __repr__(self):
        return '<%s %r (%s)>' % (self.__class__.__name__,
                                 self.name,
                                 self.direction)

    @classmethod
    def from_xml(cls, node):
        visible = node.attrib.get('visible') != 'off'
        rotate = int(node.attrib.get('rot', 'R0')[1:])
        return cls(name=node.attrib['name'],
                   pos=(float(node.attrib['x']),
                        float(node.attrib['y'])),
                   length=node.attrib['length'],
                   direction=node.attrib.get('direction'),
                   rotate=rotate,
                   visible=visible)


class Polygon(object):
    def __init__(self, width, layer, vertices=None):
        self.width = width
        self.layer = layer
        self.vertices = vertices or []

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__,
                            self.vertices)

    @classmethod
    def from_xml(cls, node):
        vertices = []
        for vertex_node in node.xpath('vertex'):
            vertices.append((float(vertex_node.attrib['x']),
                             float(vertex_node.attrib['y'])))
        return cls(width=float(node.attrib['width']),
                   layer=int(node.attrib['layer']),
                   vertices=vertices)


class Hole(object):
    def __init__(self, pos, drill):
        self.x, self.y = pos
        self.drill = drill

    def __repr__(self):
        return '<%s (%f, %f)>' % (self.__class__.__name__,
                                  self.x, self.y)

    @classmethod
    def from_xml(cls, node):
        return cls(pos=(float(node.attrib['x']),
                        float(node.attrib['y'])),
                   drill=float(node.attrib['drill']))


class Circle(object):
    def __init__(self, pos, radius, width, layer):
        self.x, self.y = pos
        self.radius = radius
        self.width = width
        self.layer = layer

    def __repr__(self):
        return '<%s (%f, %f) %f>' % (self.__class__.__name__,
                                     self.x, self.y,
                                     self.radius)

    @classmethod
    def from_xml(cls, node):
        return cls(pos=(float(node.attrib['x']),
                        float(node.attrib['y'])),
                   radius=float(node.attrib['radius']),
                   width=float(node.attrib['width']),
                   layer=int(node.attrib['layer']))


class Geometry(object):
    def __init__(self, primitives=None):
        self.primitives = primitives or []

    @staticmethod
    def geometry_from_xml(node):
        primitives = []
        for cls, tag in [(Wire, 'wire'),
                         (SMD, 'smd'),
                         (Text, 'text'),
                         (Rectangle, 'rectangle'),
                         (Polygon, 'polygon'),
                         (Pad, 'pad'),
                         (Pin, 'pin')]:
            for subnode in node.xpath(tag):
                primitives.append(cls.from_xml(subnode))
        return primitives

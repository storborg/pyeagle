import math

from lxml.etree import tostring
from lxml.builder import E


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        return ((min(self.x1, self.x2), min(self.y1, self.y2)),
                (max(self.x1, self.x2), max(self.y1, self.y2)))

    def to_svg(self, offset, scale):
        offx, offy = offset

        color = 'rgb(80, 80, 80)'
        style = 'stroke:%s;stroke-width:%d' % (color, self.width * scale)

        return [E.line(
            x1=str((self.x1 + offx) * scale),
            y1=str((self.y1 + offy) * scale),
            x2=str((self.x2 + offx) * scale),
            y2=str((self.y2 + offy) * scale),
            style=style,
        )]


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        return ((self.x - (self.dx / 2.0), self.y - (self.dy / 2.0)),
                (self.x + (self.dx / 2.0), self.y + (self.dy / 2.0)))

    def to_svg(self, offset, scale):
        offsetx, offsety = offset

        color = 'rgb(180, 0, 0)'
        style = 'fill:%s' % color

        return [E.rect(
            x=str((self.x + offsetx - (self.dx / 2.0)) * scale),
            y=str((self.y + offsety - (self.dy / 2.0)) * scale),
            width=str(self.dx * scale),
            height=str(self.dy * scale),
            style=style,
        )]


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        # FIXME Can we actually calculate this? May need to render text.
        return ((self.x, self.y),
                (self.x, self.y))

    def to_svg(self, offset, scale):
        # FIXME Implement this
        return []


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        return ((min(self.x1, self.x2), min(self.y1, self.y2)),
                (max(self.x1, self.x2), max(self.y1, self.y2)))

    def to_svg(self, offset, scale):
        offsetx, offsety = offset

        color = 'rgb(180, 0, 0)'
        style = 'fill:%s' % color

        x = min(self.x1, self.x2)
        y = min(self.y1, self.y2)
        width = abs(self.x2 - self.x1)
        height = abs(self.y2 - self.y1)

        return [E.rect(
            x=str((x + offsetx - (width / 2.0)) * scale),
            y=str((y + offsety - (height / 2.0)) * scale),
            width=str(width * scale),
            height=str(height * scale),
            style=style,
        )]


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        margin = self.diameter / 2.0
        return ((self.x - margin,
                 self.y - margin),
                (self.x + margin,
                 self.y + margin))

    def to_svg(self, offset, scale):
        # FIXME Implement this
        return []


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        # FIXME Need to render things
        return ((self.x, self.y),
                (self.x, self.y))

    def to_svg(self, offset, scale):
        # FIXME Implement this
        return []


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        margin = self.width / 2.0
        return ((min(x for x, y in self.vertices) - margin,
                 min(y for x, y in self.vertices) - margin),
                (max(x for x, y in self.vertices) + margin,
                 max(y for x, y in self.vertices) + margin))

    def to_svg(self, offset, scale):
        # FIXME Implement this
        return []


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        margin = self.drill / 2.0
        return ((self.x - margin,
                 self.y - margin),
                (self.x + margin,
                 self.y + margin))

    def to_svg(self, offset, scale):
        offsetx, offsety = offset
        color = 'rgb(20, 20, 20)'
        style = 'fill:rgba(0, 0, 0, 0);stroke:%s;stroke-width:%d' % (color, 1)

        return [E.circle(
            r=str((self.drill / 2.0) * scale),
            cx=str((self.x + offsetx) * scale),
            cy=str((self.y + offsety) * scale),
            style=style,
        )]


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

    def to_xml(self):
        """
        Serialize this primitive element to a fragment in EAGLE's XML format.
        """
        raise NotImplementedError

    def bounding_box(self):
        margin = self.radius + (self.width / 2.0)
        return ((self.x - margin, self.y - margin),
                (self.x + margin, self.y + margin))

    def to_svg(self, offset, scale):
        offsetx, offsety = offset
        color = 'rgb(20, 20, 20)'
        style = 'fill:rgba(0, 0, 0, 0);stroke:%s;stroke-width:%d' % (color, 1)

        return [E.circle(
            r=str(self.radius * scale),
            cx=str((self.x + offsetx) * scale),
            cy=str((self.y + offsety) * scale),
            style=style,
        )]


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
                         (Hole, 'hole'),
                         (Pad, 'pad'),
                         (Pin, 'pin')]:
            for subnode in node.xpath(tag):
                primitives.append(cls.from_xml(subnode))
        return primitives

    def bounding_box(self):
        startx = starty = endx = endy = 0
        for primitive in self.primitives:
            (x1, y1), (x2, y2) = primitive.bounding_box()
            startx = min(startx, x1)
            starty = min(starty, y1)
            endx = max(endx, x2)
            endy = max(endy, y2)
        return (startx, starty), (endx, endy)

    def to_svg(self, scale):
        (startx, starty), (endx, endy) = self.bounding_box()
        width = math.ceil((endx - startx) * scale)
        height = math.ceil((endy - starty) * scale)

        offset = (-startx, -starty)

        children = []
        for primitive in self.primitives:
            children.extend(primitive.to_svg(offset, scale))

        root = E.svg(
            *children,
            width=str(width),
            height=str(height))
        return tostring(root)

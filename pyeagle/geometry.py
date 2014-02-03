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
        return cls(start=(node.attrib['x1'],
                          node.attrib['y1']),
                   end=(node.attrib['x2'],
                        node.attrib['y2']),
                   width=node.attrib['width'],
                   layer=node.attrib['layer'],
                   curve=node.attrib.get('curve'),
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
                   pos=(node.attrib['x'],
                        node.attrib['y']),
                   size=(node.attrib['dx'],
                         node.attrib['dy']),
                   layer=node.attrib['layer'])


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
        return cls(s=node.text,
                   pos=(node.attrib['x'],
                        node.attrib['y']),
                   size=node.attrib['size'],
                   layer=node.attrib['layer'],
                   ratio=node.attrib.get('ratio'))


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
        return cls(start=(node.attrib['x1'],
                          node.attrib['y1']),
                   end=(node.attrib['x2'],
                        node.attrib['y2']),
                   layer=node.attrib['layer'])


class Geometry(object):
    def __init__(self, primitives=None):
        self.primitives = primitives or []

    @staticmethod
    def geometry_from_xml(node):
        primitives = []
        for cls, tag in [(Wire, 'wire'),
                         (SMD, 'smd'),
                         (Text, 'text'),
                         (Rectangle, 'rectangle')]:
            for subnode in node.xpath(tag):
                primitives.append(cls.from_xml(subnode))
        return primitives

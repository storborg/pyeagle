"""
Helpers to manage EAGLE layer definitions, for rendering objects into 2D
geometry with appropriate colors and visibility.
"""

from . import colors


class LayerSet(object):
    """
    Represents a set of layer definitions for an EAGLE drawing, controlling
    things like name, visibility, color, and fill style.
    """
    def __init__(self, layers=None):
        self.layers = layers or {}
        self.layers_by_name = {layer.name: layer for layer in
                               self.layers.values()}

    @classmethod
    def from_xml(cls, node):
        """
        Construct a LayerSet instance fron an EAGLE XML ``<layers>`` node.
        """
        layers = {}
        for layer_node in node.xpath('layer'):
            layer = Layer.from_xml(layer_node)
            layers[int(layer.number)] = layer
        return cls(layers=layers)

    def to_xml(self):
        """
        Serialize this to an EAGLE XML node.
        """
        raise NotImplementedError

    def is_visible(self, number):
        layer = self.layers[number]
        return layer.active and layer.visible

    def get_css_color(self, number):
        if self.is_visible(number):
            layer = self.layers[number]
            return colors.as_css(layer.color)


class Layer(object):
    """
    Represents a single layer definition for an EAGLE drawing.
    """
    def __init__(self, number, name=u'Untiitled', color=1, visible=True,
                 active=True):
        self.number = number
        self.name = name
        self.color = color
        self.visible = visible
        self.active = active

    @classmethod
    def from_xml(cls, node):
        """
        Construct a Layer instance from an EAGLE XML ``<layer>`` node.
        """
        return cls(
            number=int(node.attrib['number']),
            name=node.attrib['name'],
            color=int(node.attrib['color']),
            visible=(node.attrib['visible'] == 'yes'),
            active=(node.attrib['active'] == 'yes'),
        )

    def to_xml(self):
        """
        Serialize this to an EAGLE XML node.
        """
        raise NotImplementedError

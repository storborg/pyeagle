import math

from lxml.etree import tostring
from lxml.builder import E


svg_preamble = '<?xml version="1.0" encoding="utf-8" standalone="no"?>'


def css_encode(d):
    return ';'.join('%s:%s' % (k, v) for k, v in d.items())


class SVGRenderer(object):
    def __init__(self, primitive, layers, scale=1, margin=10,
                 flip=(1, -1), add_bounding_box=True):
        self.primitive = primitive
        self.scale = scale
        self.layers = layers
        self.margin = margin
        self.flip = flip
        self.add_bounding_box = add_bounding_box

    def to_svg_bounding_box(self, thing):
        flipx, flipy = self.flip
        (startx, starty), (endx, endy) = thing.bounding_box()
        width = math.ceil((endx - startx) * self.scale)
        height = math.ceil((endy - starty) * self.scale)

        style = css_encode({
            'stroke-width': 1,
            'stroke': 'red',
            'fill': 'rgba(255, 0, 0, 0.1)',
        })

        return E.rect(
            x=str(self.margin),
            y=str(self.margin),
            width=str(width),
            height=str(height),
            style=style,
        )

    def make_svg_doc(self):
        (startx, starty), (endx, endy) = self.primitive.bounding_box()

        native_width = endx - startx
        native_height = endy - starty

        scaled_width = math.ceil(native_width * self.scale)
        scaled_height = math.ceil(native_height * self.scale)

        offset_margin = float(self.margin) / self.scale

        offsetx = (-startx)
        offsety = (-starty)

        flipx, flipy = self.flip

        if flipy == 1:
            offsety = -starty
        elif flipy == -1:
            offsety = native_height + starty

        if flipx == 1:
            offsetx = -startx
        elif flipx == -1:
            offsetx = native_width + startx

        offsetx += offset_margin
        offsety += offset_margin

        offset = offsetx, offsety

        children = self.primitive.to_svg_fragments(offset, self.scale,
                                                   self.flip, self.layers)

        if self.add_bounding_box:
            children.insert(0, self.to_svg_bounding_box(self.primitive))

        root = E.svg(
            *children,
            width=str(scaled_width + (2 * self.margin)),
            height=str(scaled_height + (2 * self.margin)))
        return tostring(root).decode('utf8')

    def render_to_string(self):
        return self.make_svg_doc()

    def save(self, filename):
        s = svg_preamble + '\n' + self.make_svg_doc()
        with open(filename, 'w') as f:
            f.write(s)

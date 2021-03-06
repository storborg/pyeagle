from lxml import etree

from . import types

__version__ = '0.1.2.dev'


def open(f):
    """
    The main PyEAGLE entry point, to load an EAGLE object from a filename or
    file-like object.

    :param f:
        Filename or file-like object.
    :returns:
        Corresponding PyEAGLE object for the type of file.
    """
    tree = etree.parse(f)
    root = tree.getroot()

    # FIXME Add file identification for design rules, autorouter rules, CAM
    # jobs, ULPs.
    for tag, cls in [('library', types.Library),
                     ('schematic', types.Schematic),
                     ('board', types.Board)]:
        nodes = root.xpath('drawing/' + tag)
        if len(nodes) == 1:
            node = root.xpath('drawing')[0]
            return cls.from_drawing_xml(node, from_file=f)
    raise NotImplementedError

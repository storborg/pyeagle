from lxml import etree

from . import types


def open(f):
    """
    The main PyEAGLE entry point, to load an EAGLE object from a filename or
    file-like object.

    Only supports .lbr files so far.

    :param f:
        Filename or file-like object.
    :returns:
        Corresponding PyEAGLE object for the type of file.
    """
    tree = etree.parse(f)
    root = tree.getroot()

    for tag, cls in [('library', types.Library),
                     ('schematic', types.Schematic),
                     ('board', types.Board)]:
        nodes = root.xpath('drawing/' + tag)
        if len(nodes) == 1:
            return cls.from_xml(nodes[0], from_file=f)
    raise NotImplementedError

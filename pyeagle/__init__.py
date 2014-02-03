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

    lib_roots = root.xpath('drawing/library')
    if len(lib_roots) == 1:
        return types.Library.from_xml(lib_roots[0], from_file=f)
    else:
        raise NotImplementedError

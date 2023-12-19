import os


class DevError(RuntimeError):
    def __init__(self, msg):
        RuntimeError.__init__(self, "programming error: %s" % msg)


def xml_escape(xml: str) -> str:
    """
    Replaces chars ' " < > & with xml safe counterparts
    """
    if xml:
        xml = xml.replace("&", "&amp;")
        xml = xml.replace("'", "&apos;")
        xml = xml.replace("\"", "&quot;")
        xml = xml.replace("<", "&lt;")
        xml = xml.replace(">", "&gt;")
    return xml


def get_prop_path(obj, prop_path: str):
    """Return value of attribute identified by `prop_path`

    Look up the attribute of `obj` identified by `prop_path`
    (separated by "."). If any component along the path is missing an
    `AttributeError` is raised.

    """
    parent = obj
    pieces = prop_path.split(".")
    for piece in pieces[:-1]:
        parent = getattr(parent, piece)

    return getattr(parent, pieces[-1])


def set_prop_path(obj, prop_path, value):
    """Set value of attribute identified by `prop_path`

    Set the attribute of `obj` identified by `prop_path` (separated by
    ".") to `value`. If any component along the path is missing an
    `AttributeError` is raised.
    """
    parent = obj
    pieces = prop_path.split(".")
    for piece in pieces[:-1]:
        parent = getattr(parent, piece)

    return setattr(parent, pieces[-1], value)


def get_difference(origin_str, new_str, from_file="Original", to_file="New") -> str:
    """
    find the difference between two strings, return a str indicating the changes
    """
    import difflib
    dlist = difflib.unified_diff(
        origin_str.splitlines(1), new_str.splitlines(1),
        fromfile=from_file, tofile=to_file)
    return "".join(dlist)


def unindent_device_xml(xml: str) -> str:
    """
    remove indent from device xml strs
    """
    import re
    lines = xml.splitlines()
    if not lines:
        return xml  # pragma: no cover

    ret = ""
    unindent = 0
    for c in lines[0]:
        if c != " ":
            break
        unindent += 1

    for line in lines:
        if re.match(r"^%s *<.*$" % (unindent * " "), line):
            line = line[unindent:]
        ret += line + "\n"
    return ret

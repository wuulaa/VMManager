import lxml.etree as etree
import src.Utils.XMLBuilder.xml_utils as xml_utils
import src.Utils.global_ns_map as global_ns_map
from src.Utils.XMLBuilder.xml_utils import DevError
from lxml.etree import ElementBase
from typing import List


class _XPathSegment:
    """
        Class representing a single 'segment' of a xpath string. For example,
        the xpath:

            ./qemu:foo/bar[1]/baz[@somepro='someval']/@finalprop

        will be split into the following segments:

            #1: node_name=., full_segment=.
            #2: node_name=foo, nsname=qemu, full_segment=qemu:foo
            #3: node_name=bar, condition_num=1, full_segment=bar[1]
            #4: node_name=baz, condition_prop=somepro, condition_val=someval,
                    full_segment=baz[@somepro='somval']
            #5: node_name=finalprop, is_prop=True, full_segment=@finalprop
        """
    '''
    variable list:
    self.full_segment: str = None
    self.node_name: str = None
    self.condition_num: int = None
    self.condition_prop: str = None
    self.condition_val: str = None
    self.is_prop: bool = False
    self.ns_name: str = None
    '''

    def __init__(self, segment: str):
        self.full_segment: str = None
        self.node_name: str = None
        self.condition_num: int = None
        self.condition_prop: str = None
        self.condition_val: str = None
        self.is_prop: bool = False
        self.ns_name: str = None

        self.full_segment: str = segment
        self.node_name: str = segment

        if "[" in self.node_name:
            split_name = self.node_name.strip("]").split("[")
            self.node_name = split_name[0].strip()
            cond = split_name[1].strip()
            if "=" in cond:
                split_cond = cond.split("=")
                prop = split_cond[0].strip()
                val = split_cond[1].strip()
                self.condition_prop = prop.strip("@")
                self.condition_val = val.strip("'")
            elif cond.isdigit():
                self.condition_num = int(cond)

        self.is_prop = self.node_name.startswith("@")
        if self.is_prop:
            self.node_name = self.node_name[1:]

        if ":" in self.node_name:
            self.ns_name, self.node_name = self.node_name.split(":")


class _XPath:
    """
    Helper calss for manipulating XPath strings. It splits the xpath into segments above.
    """
    ''' variable list
    self.full_xpath: str = None
    self.segments: List[_XPathSegment] = []
    self.is_prop: bool = None
    self.prop_name: str = None
    self.xpath: str = None
    '''

    def __init__(self, full_xpath: str):

        self.full_xpath = full_xpath
        self.segments = []
        for s in self.full_xpath.split("/"):
            if s == "..":
                self.segments = self.segments[:-1]
                continue
            self.segments.append(_XPathSegment(s))

        self.is_prop = self.segments[-1].is_prop
        self.prop_name = (self.is_prop and self.segments[-1].node_name or None)
        # if self.is_prop:
        #     self.segments = self.segments[:-1]
        self.xpath = self.join(self.segments)

    @staticmethod
    def join(segments: List[_XPathSegment]) -> str:
        return "/".join(s.full_segment for s in segments)

    def parent_xpath(self):
        return self.join(self.segments[:-1])


###################
# node operations #
###################
def node_to_xml(node: ElementBase) -> str:
    return etree.tostring(node, pretty_print=True, encoding='unicode')


def node_from_xml(xml: str) -> ElementBase:
    node: ElementBase = etree.XML(xml)
    return node


def get_text(node: ElementBase) -> str:
    content: str = node.text
    return content


def set_text(node: ElementBase, text: str):
    if text is not None:
        text = xml_utils.xml_escape(text)
    node.text = text


def get_property(node: ElementBase, prop_name: str) -> str:
    return node.get(prop_name)


def set_property(node: ElementBase, prop_name: str, prop_val: str):
    node.set(prop_name, prop_val)


def clear(node: ElementBase):
    if node is not None:
        node.clear()


def has_content(node: ElementBase) -> bool:
    """
    Determine whether a node is empty by children or text content or properties
    """
    return node.text is not None or len(node.getchildren()) > 0 or len(node.keys()) > 0


def create_node_from_tag(tag: str) -> ElementBase:
    return etree.Element(tag)


def create_node_with_namespace(tag: str, prefix: str, uri: str, root_node: ElementBase = None):
    if prefix is None and uri is not None:
        ns = "{%s}" % uri
        if uri in global_ns_map.get_ns_map().values():
            element: ElementBase = etree.Element(ns + tag)
        else:
            nsmap = {None: uri}
            element: ElementBase = etree.Element(ns + tag, nsmap=nsmap)
        return element

    if prefix is not None and uri is None:
        if root_node is not None and prefix in root_node.nsmap:
            uri = root_node.nsmap[prefix]
            global_ns_map.register_namespace(prefix, uri)
            nsmap = {prefix: uri}
            return etree.Element(tag, nsmap=nsmap)
        elif prefix in global_ns_map.get_ns_map().keys():
            uri = global_ns_map.get_ns_map()[prefix]
            global_ns_map.register_namespace(prefix, uri)
            nsmap = {prefix: uri}
            return etree.Element(tag, nsmap=nsmap)
        else:
            raise xml_utils.DevError("XML namespace not registered")

    nsmap = {prefix: uri}
    element: ElementBase = etree.Element(tag, nsmap=nsmap)
    return element


def get_tag(node: ElementBase):
    return node.tag


def get_root(node: ElementBase) -> ElementBase:
    parent: ElementBase = node.getparent()
    while parent is not None:
        parent = node.getparent()
    return parent


def get_parent(node: ElementBase) -> ElementBase:
    return node.getparent()


def get_children(node: ElementBase) -> List[ElementBase]:
    return node.getchildren()


def remove_child(parent_node: ElementBase, child_node: ElementBase):
    parent_node.remove(child_node)


def add_child(parent_node: ElementBase, new_node: ElementBase):
    parent_node.append(new_node)


def replace_child(node: ElementBase, old_node: ElementBase, new_node: ElementBase):
    node.replace(old_node, new_node)


def remove_self(node: ElementBase):
    parent_node: ElementBase = node.getparent()
    # Can not remove a root node, so just directly set it to None
    if parent_node is None:
        node = None
    parent_node.remove(node)
    node = None


####################
# xpath operations #
####################
def find_first(node: ElementBase, full_xpath: str):
    """
    Find a node or value based on a xpath
    """
    ns: dict = node.nsmap.copy()
    ns.update(global_ns_map.get_ns_map())
    nodes: list = node.xpath(full_xpath, namespaces=ns)
    if len(nodes) == 0:
        return None
    return nodes[0]


def find_all(node: ElementBase, full_xpath: str) -> list:
    ns: dict = node.nsmap.copy()
    ns.update(global_ns_map.get_ns_map())
    nodes: list = node.xpath(full_xpath, namespaces=ns)
    return nodes


def count(base_node: ElementBase, xpath: str) -> int:
    """
    Count the number of xml nodes that fits the xpath description
    """
    nodes = base_node.findall(xpath)
    return len(nodes)


def create_node_from_xpath_segment(parent_node: ElementBase, segment: _XPathSegment) -> ElementBase:
    # Simply add an attribute if the xpath segment indicates an attribute.
    # The value of this attribute would be an empty string
    if segment.is_prop:
        set_property(parent_node, segment.node_name, '')
        return parent_node

    if segment.ns_name is not None:
        new_node: ElementBase = create_node_with_namespace(segment.node_name, segment.ns_name, uri=None,
                                                           root_node=parent_node)
        add_child(parent_node, new_node)
        return new_node

    new_node: ElementBase = create_node_from_tag(segment.node_name)
    if segment.condition_prop is not None:
        new_node.set(segment.condition_prop, segment.condition_val)
    add_child(parent_node, new_node)
    return new_node


def get_xpath_content(base_node: ElementBase, xpath: str):
    """
    Get the content of xpath, regularly return the text of the node.
    If xpath points to a property, return the value of the property.
    Note that this only gets the first match.
    base_node: root node where the search begins

    """
    node: ElementBase = base_node.find(xpath)
    if node is None:
        return None
    xpath_obj = _XPath(xpath)
    if xpath_obj.is_prop:
        return node.get(xpath_obj.prop_name)
    return node.text


def set_xpath_content(base_node: ElementBase, xpath: str, value) -> bool:
    node: ElementBase = find_first(base_node, xpath)
    if node is None:
        return False
    xpath_obj = _XPath(xpath)
    if value is None:
        # remove the node if the value to be set is None
        node.clear()
        remove_self(node)
    else:
        value = str(value)
        if xpath_obj.is_prop:
            node.set(xpath_obj.prop_name, value)
        else:
            node.text = value
    return True


def build_sub_node_from_xpath(base_node: ElementBase, xpath: str) -> ElementBase:
    """
    Build all nodes for the passed xpath. For example, if base XML is <foo/>,
    and xpath=./bar/@baz, after this function the XML will be:

      <foo>
        <bar baz=''/>
      </foo>

    And the node pointing to @baz will be returned, for the caller to
    do with as they please.

    There's also special handling to ensure that setting
    xpath=./bar[@baz='foo']/frob will create

      <bar baz='foo'>
        <frob></frob>
      </bar>

    Even if <bar> didn't exist before. So we fill in the dependent property
    expression values

    ATTENTION: do not use "../" in the xpath parameter, creation via xpath
    should only be towards the child.
    """
    if '../' in xpath:
        raise (
            "Do not use '../' in xpath argument, creation via xpath should only be towards the child")
    xpath_obj = _XPath(xpath)
    segments = xpath_obj.segments
    parent_path = "."
    parent_node = find_first(base_node, parent_path)
    if parent_node is None:
        raise DevError("Did not find xml root node for xpath = %s" % xpath)

    for segment in segments[1:]:
        path = "." + "/%s" % segment.full_segment
        tmp_node = find_first(parent_node, path)
        if tmp_node is not None:
            # node already exists, create nothing
            parent_node = tmp_node
            continue
        new_node = create_node_from_xpath_segment(parent_node, segment)
        parent_node = new_node

    return parent_node

# NameSpaces = {}
#
#
# bookstore = """
# <bookstore xmlns:a="www.song.com">
#     <a:book category="CHILDREN" xmlns:b="www.ssss.com">
#         <a:title>Harry Potter</a:title>
#         <author>J K. Rowling</author>
#         <year>2005</year>
#         <price>29.99</price>
#     </a:book>
#     <book category="WEB">
#         <title>Learning XML</title>
#         <author>Erik T. Ray</author>
#         <year>2003</year>
#         <price>39.95</price>
#     </book>
# </bookstore>"""
#
# root: ElementBase = etree.XML(bookstore)
# print(root.nsmap)
#
# ca: ElementBase = find_first(root, ".//a:book")
# print(ca)
# title = find_first(ca, ".//a:title")
# print(title)
#
# newnode = create_node_with_namespace("aaa", None, uri="www.666.cc", root_node=root)
# add_child(root, newnode)
# print(node_to_xml(root))
# print(newnode.nsmap)
# book1: ElementBase = root.getchildren()[0]
# print(root)
# build_sub_node_from_xpath(root, "./@name")
# build_sub_node_from_xpath(root, "./@ame")
# print(node_to_xml(root))
#
# # book1.getparent().remove(book1)
# # print(node_tostring(book1))
# # print(node_tostring(root))
#
# # xmlapi = _LXMLAPI(bookstore)
# # count = xmlapi.count(".//a")
# # print(count)
# # book = xmlapi.find(".//book")
# # print(xmlapi.node_tostring(book))
# #
# # author = book.find("./author")
# # text = xmlapi.node_get_text(author)
# # print(text)
# # xmlapi.node_set_text(author, "york")
# # print(xmlapi.node_get_text(author))
# #
# # print(xmlapi.node_get_property(book, "category"))
# # xmlapi.node_set_property(book,"category","AAAAA")
# # print(xmlapi.node_get_property(book, "category"))
# #
# # print(xmlapi.node_remove_child(book,author))
# # print(book.getchildren())
# #
# # store = etree.fromstring(bookstore)
# # print(etree.tostring(store, encoding='unicode', pretty_print=True))
# e = create_tag_with_namespace("aaa", "p", "uriuriuri")
# print(node_to_xml(e))

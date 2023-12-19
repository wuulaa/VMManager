import random
from typing import List, Dict
from src.Utils.XMLBuilder import xml_api, xml_utils
from lxml.etree import ElementBase
import libvirt
import src.Utils.global_ns_map as gnm
import uuid

class XMLPropertyBase(property):
    """
    Base class for XMLProperty and XMLChildBuilder, currently useless.
    Inheriting property class, so it can be regarded as a class's property
    after declaration. In this case, they can be accessed using class.property
    pattern.
    """
    def __init__(self, getter, setter):
        super().__init__(fget=getter, fset=setter)
        self._prop_name: str = ""

    @property
    def prop_name(self):
        return self._prop_name


class XMLChildBuilder(XMLPropertyBase):
    """
    Child builder within a XMLBuilder, enable the nesting of builders.
    """

    UID_set: dict = {}

    def __init__(self, child_class, relative_xpath=".", is_single=True):
        """
        Init a child XMLBuilder, should only be declared as a class property.
        Do not declare in XMLBuilder's __init__() function as object property.
        Note that declare would not construct the xml.
        Set a child XMLBuilder object in the parent builder object to actually
        construct the xml. See the example code below for usage

        :param child_class: the class of XMLBuilder to be nested
        :param relative_xpath: relative path to the parent, could wrap child builder in tags
        :param is_single: indicating whether the nested builder is single or a list.
            For single children, use '.' to directly get and set. For children list,
            use append(builder), get(index), set(index, builder), or []
        """
        self.child_class: XMLChildBuilder.__class__ = child_class
        self.is_single = is_single
        if relative_xpath != '.' and (relative_xpath.find("./") == -1 or relative_xpath.find("@") != -1):
            raise xml_utils.DevError("The relative path of XMLChildBuilder should be like './a/b' ")
        self.relative_xpath = relative_xpath
        # The actual nested XMLBuilder for single child
        self.parent2Builder_set: dict = {}
        # The actual nested XMLBuilders for non-single child
        self.parent2builder_list_set: dict = {}
        # The parent XMLBuilder of this child
        self.parent_builder: XMLBuilder = None


        self.builder2Parent_set: dict = {}

        super().__init__(self._prop_getter, self._prop_setter)

    def _prop_getter(self, parent_builder):
        """
        Getter function to be set in super().__init__(),
        return the actual XMLBuilder for single ones,
        return XMLChildBuilder itself for non-single ones.
        """
        cache_name = self.child_class.__name__ + str(parent_builder.get_uuid())
        self.parent_builder = parent_builder
        if self.is_single:
            return self.parent2Builder_set.get(cache_name)
        else:
            return self

    def _prop_setter(self, parent_builder, value):
        """
        Setter function to be set in super().__init__(),
        works only for single ones.
        """
        if not self.is_single:
            raise xml_utils.DevError("Unable to directly set a not single child builder, use append() or set() instead")

        cache_name = self.child_class.__name__ + str(parent_builder.get_uuid())
        # If value is None, remove the existing child builder
        if value is None:
            parent_builder: XMLBuilder = parent_builder
            if self.parent2Builder_set.get(cache_name) is None:
                return
            else:
                parent_builder.remove_child(cache_name, relative_xpath=self.relative_xpath)
                return

        if type(value) is not self.child_class:
            raise xml_utils.DevError("Wrong type, value should have the same type as XMLChildBuilder's child_class")

        builder_to_be_set: XMLBuilder = value
        parent_builder: XMLBuilder = parent_builder
        self.parent_builder = parent_builder
        # If the actual builder does not exist, construct the xml.
        # # Otherwise replace the old xml with the new one.
        if self.parent2Builder_set.get(cache_name) is not None:
            self.parent2Builder_set[cache_name] = builder_to_be_set
            parent_builder.replace_child(cache_name, builder_to_be_set, relative_xpath=self.relative_xpath)
        else:
            self.parent2Builder_set[cache_name] = builder_to_be_set
            parent_builder.add_child(cache_name, builder_to_be_set,relative_xpath=self.relative_xpath)

    def append(self, child_builder):
        """
        Used for non-single child, append a new builder to the children list
        :param child_builder: the appended builder
        """
        if self.is_single:
            raise xml_utils.DevError("Wrong usage, append() could only be used for non-single XMLChildBuilder")

        if type(child_builder) is not self.child_class:
            raise xml_utils.DevError("Wrong type, value should have the same type as XMLChildBuilder's child_class")

        # For non-single child, each builder in the child list would have a unique
        # id for identifying.
        cache_name = self.child_class.__name__ + str(child_builder.get_uuid())
        parent_cache_name = self.child_class.__name__ + str(self.parent_builder.get_uuid())

        self.parent_builder.add_child(cache_name, child_builder, relative_xpath=self.relative_xpath)

        if self.parent2builder_list_set.get(parent_cache_name) is None:
            self.parent2builder_list_set[parent_cache_name] = []
        self.parent2builder_list_set.get(parent_cache_name).append(child_builder)
        self.UID_set[cache_name] = child_builder

    def get(self, index: int):
        """
        Used for non-single child, get a builder from children list
        :param index: index in the list
        """
        parent_cache_name = self.child_class.__name__ + str(self.parent_builder.get_uuid())
        if self.is_single:
            raise xml_utils.DevError("Wrong usage, get() could only be used for non-single XMLChildBuilder")
        builder_list = self.parent2builder_list_set.get(parent_cache_name)
        if builder_list is None:
            raise xml_utils.DevError("Index exceeds the list length, get a None list")
        return builder_list[index]

    def set(self, index: int, child_builder):
        """
        Used for non-single child, set a builder of children list
        :param index: index of the builder
        :param child_builder: value to be set
        """
        parent_cache_name = self.child_class.__name__ + str(self.parent_builder.get_uuid())
        builder_list = self.parent2builder_list_set.get(parent_cache_name)
        if self.is_single:
            raise xml_utils.DevError("Wrong usage, set() could only be used for non-single XMLChildBuilder")
        if len(builder_list) < index + 1:
            raise xml_utils.DevError("Index exceeds the list length")

        old_builder: XMLBuilder = builder_list[index]
        # Get the cache_name of the old builder, ensuring that old and new builder are mapped to the
        # same uid
        cache_name = list(self.UID_set.keys())[list(self.UID_set.values()).index(old_builder)]
        if child_builder is None:
            self.parent_builder.remove_child(cache_name, relative_xpath=self.relative_xpath)
            builder_list.pop(index)
            self.UID_set.pop(cache_name)
            return
        elif type(child_builder) is not self.child_class:
            raise xml_utils.DevError("Wrong type, value should have the same type as XMLChildBuilder's child_class")
        self.parent_builder.replace_child(cache_name, child_builder, relative_xpath=self.relative_xpath)
        builder_list[index] = child_builder
        self.UID_set[cache_name] = child_builder
        self.parent2builder_list_set[parent_cache_name] = builder_list

    def _generate_uid(self) -> str:
        """
        Helper function to generate a 32 length str uid
        :return:
        """
        uid = ""
        for i in range(32):
            digit = random.randint(0, 1)
            uid += str(digit)
        uid = int(uid)
        while self.child_class.__name__ + str(uid) in self.UID_set.keys():
            uid += 1
        return str(uid)

    def __getitem__(self, index: int):
        """
        Override [], see example below
        """
        return self.get(index)

    def __setitem__(self, index: int, child_builder):
        """
        Override [], see example below
        """
        self.set(index, child_builder)


class XMLProperty(XMLPropertyBase):
    """
    Object Variable list
    _xpath: str = None
    _is_bool: bool = False
    _is_int: bool = False
    _is_yesno: bool = False
    _is_onoff: bool = False
    _is_openclose: bool = False

    """

    def __init__(self, xpath: str, is_bool: bool = False, is_int: bool = False,
                 is_yesno: bool = False, is_onoff: bool = False, is_openclose: bool = False):
        """
        Property within a XMLBuilder, could be a xml attribute using '@' in the xpath,
        or a simple content. Note that declare would not construct the xml.
        Set the property using '.' expression in the builder object to actually construct.
        See the example code below for usage.
        :param xpath: the relative xpath string
        :param is_bool: whether the value would be a bool
        :param is_int: whether the value would be an int
        :param is_yesno: whether the value would be a "yes/no"
        :param is_onoff: whether the value would be a "on/off"
        """
        if xpath is None:
            raise xml_utils.DevError("XMLProperty: xpath must be passed.")
        self._xpath: str = xpath
        self._content: str = None
        self._is_bool: bool = is_bool
        self._is_int: bool = is_int
        self._is_yesno: bool = is_yesno
        self._is_onoff: bool = is_onoff
        self._is_openclose: bool = is_openclose

        self.is_prop = False
        if "/@" in self._xpath:
            self.is_prop = True

        super().__init__(getter=self._prop_getter, setter=self._prop_setter)



    def get_xpath(self):
        return self._xpath

    def get_content(self):
        return self._content

    def set_content(self, val):
        self._content = val

    def _convert_get_value(self, val: str):
        ret = None
        if self._is_bool:
            return bool(val)
        elif self._is_int and val is not None:
            try:
                intkwargs = {}
                if "0x" in str(val):
                    intkwargs["base"] = 16
                ret = int(val, **intkwargs)
            except ValueError as e:
                ret = val
        elif self._is_yesno:
            if val == "yes":
                ret = True
            elif val == "no":
                ret = False
            else:
                return val
        elif self._is_onoff:
            if val == "on":
                ret = True
            elif val == "off":
                ret = False
            else:
                ret = val
        elif self._is_openclose:
            if val == "open":
                ret = True
            elif val == "close":
                ret = False
            else:
                ret = val
        else:
            ret = val
        return ret

    def _convert_set_value(self, val):
        if self._is_onoff:
            if val is True:
                val = "on"
            else:
                val = "off"
        elif self._is_yesno:
            if val is True:
                val = "yes"
            else:
                val = "no"
        elif self._is_int and val is not None:
            int_kwargs = {}
            if "0x" in str(val):
                int_kwargs["base"] = 16
            val = str(val, **int_kwargs)
        elif self._is_openclose:
            if val is True:
                val = "open"
            else:
                val = "close"
        return val

    def get_value_from_xml(self, xml_builder):
        """
        Actually fetch the value of this property from parent XMLBuilder's xml
        """
        value = xml_api.find_first(xml_builder.xml, self._xpath)
        if self.is_prop:
            return self._convert_get_value(value)
        else:
            if value is not None:
                return value.text
            return value

    def set_value_to_xml(self, xml_builder, value):
        """
        Actually set the value of this property to parent XMLBuilder's xml
        """
        if value is None:
            return
        value = self._convert_set_value(value)
        if self.is_prop:
            prop_index = self._xpath.find("@")
            prop_name = self._xpath.strip()[prop_index + 1:]

            parent_path = self._xpath.strip()[0:prop_index-1]
            parent = xml_api.find_first(xml_builder.xml, parent_path)
            if parent is not None:
                xml_api.set_property(parent, prop_name, value)
            else:
                xml_api.build_sub_node_from_xpath(xml_builder.xml, self.get_xpath())
                parent = xml_api.find_first(xml_builder.xml, parent_path)
                xml_api.set_property(parent, prop_name, value)
        else:
            node = xml_api.find_first(xml_builder.xml, self.get_xpath())
            if node is not None:
                xml_api.set_xpath_content(xml_builder.xml, self._xpath, value)
            else:
                xml_api.build_sub_node_from_xpath(xml_builder.xml, self.get_xpath())
                xml_api.set_xpath_content(xml_builder.xml, self._xpath, value)

    def _prop_getter(self, builder):
        """
        Getter function to be set in super().__init__()
        """
        return self.get_value_from_xml(builder)

    def _prop_setter(self, builder, value):
        """
        Setter function to be set in super().__init__()
        """
        self._content = value
        self.set_value_to_xml(builder, value)


class XMLBuilder:
    """
    Helper class to construct xml, it should have XMLProperty as its property
    Also use XMLChildBuilder for nested XMLBuilder
    """

    # Name to be override in children classes. It serves as the root tag of a xml
    XML_NAME: str = "BUILDER"
    XML_PROP_ORDER: List[str] = []

    def __init__(self,
                 conn: libvirt.virConnect = None,
                 cond = None):
        """
        Init a XMLBuilder. Remember to pass the cond param if you want to set the
        default values of its XMLProperty and XMLChildBuilder
        :param conn: currently usess
        :param cond: param for set_defaults
        """
        self._xml_props: Dict[str, XMLProperty] = {}
        self._children_builders: Dict[str, XMLBuilder] = {}
        self.connection: libvirt.virConnect = conn
        if ":" in self.XML_NAME:
            splits = self.XML_NAME.split(":")
            prefix = splits[0]
            tag = splits[1]
            uri = gnm.get_ns_map().get(prefix)
            self.xml: ElementBase = xml_api.create_node_with_namespace(tag, prefix, uri)
        else:
            self.xml: ElementBase = xml_api.create_node_from_tag(self.XML_NAME)
        self.set_defaults(cond=cond)

        self._uuid = uuid.uuid1()

    def get_uuid(self):
        return self._uuid

    def set_prop_cache(self, key: str, xml_property: XMLProperty):
        self._xml_props[key] = xml_property

    def get_xml_string(self) -> str:
        """
        Get the xml string of this XMLBuilder
        :return: a well formatted string of XMLBuilder's xml in unicode.
        """
        return xml_api.node_to_xml(self.xml)

    def clear(self):
        xml_api.clear(self.xml)

    def set_defaults(self, cond=None):
        """
        Function to be override in children classes, set defaults values of
        XMLProperty and XMLChildBuilder of the builder.
        :param cond: a parameter of any kind. Passed in the constructor. Be bold to use it.
        """
        pass

    def get_all_xml_props(self):
        return self._xml_props

    def get_prop(self, prop_name: str):
        return self._xml_props.get(prop_name)

    def get_all_children(self):
        return self._children_builders

    def find_child(self, child_name: str):
        return self._children_builders.get(child_name)

    def add_child(self, child_name: str, child_builder, relative_xpath: str = None):
        if relative_xpath is not None:
            relative_node: ElementBase = xml_api.find_first(self.xml, relative_xpath)
            if relative_node is None:
                xml_api.build_sub_node_from_xpath(self.xml, relative_xpath)
                relative_node = xml_api.find_first(self.xml, relative_xpath)
            xml_api.add_child(relative_node, child_builder.xml)
        else:
            xml_api.add_child(self.xml, child_builder.xml)

        self._children_builders[child_name] = child_builder

    def remove_child(self, child_name: str, relative_xpath: str = None):
        child_builder = self.find_child(child_name)
        if relative_xpath is not None:
            relative_node: ElementBase = xml_api.find_first(self.xml, relative_xpath)
            xml_api.remove_child(relative_node, child_builder.xml)
            # remove the relative note if it has no more children
            if not relative_node.getchildren():
                xml_api.remove_child(self.xml, relative_node)
        else:
            xml_api.remove_child(self.xml, child_builder.xml)
        self._children_builders.pop(child_name)

    def replace_child(self, old_child_name: str, new_child, relative_xpath: str = None):
        old_child_builder = self.find_child(old_child_name)
        if relative_xpath is not None:
            relative_node: ElementBase = xml_api.find_first(self.xml, relative_xpath)
            xml_api.replace_child(relative_node, old_child_builder.xml, new_child.xml)
        else:
            xml_api.replace_child(self.xml, old_child_builder.xml, new_child.xml)
        self._children_builders[old_child_name] = new_child

########
#示例代码#
########
# class Test(XMLBuilder):
#     XML_NAME = "Test"
#     a = XMLProperty("./a")
#     b = XMLProperty("./@b")
#
#     # set defaults 用于设置默认值， cond可以是任意类型，在XMLBuilder子类中重载以实现自己的默认值设置，
#     # cond参数在可构造函数中传入
#     def set_defaults(self, cond=None):
#         self.a = cond
#         self.b = "666"
#
#
# class Test2(XMLBuilder):
#     XML_NAME = "test2"
#     a = XMLProperty("./a")
#
#     # set defaults 用于设置默认值， cond可以是任意类型，在XMLBuilder子类中重载以实现自己的默认值设置，
#     # cond参数在可构造函数中传入
#     def set_defaults(self, cond=None):
#         self.a = "what"
#
#
# class Parent(XMLBuilder):
#     XML_NAME = "Parent"
#
#     # 声明 property, 声明不会自动构造
#     m = XMLProperty("./@m")
#
#     #声明子 builder, 声明不会自动构造, is_sigle 标识此child为单个或是数组
#     t = XMLChildBuilder(Test, is_single=False, relative_xpath="./rla")
#     t2 = XMLChildBuilder(Test2, is_single=True)
#
#
#     def set_defaults(self, cond=None):
#         #在set_defaults中赋值才会构造对应的xml
#         self.m = "m"
#         #对于非single的ChildBuilder,使用append,get(index),set(index,value)
#         self.t.append(Test(cond="444"))
#         self.t.append(Test(cond="555"))
#         self.t.set(1, Test(cond="666"))
#         #对于single的ChildBuilder,直接使用 . 进行get,set
#         self.t2 = Test2()
#
#
# # set_defaluts的cond参数在可构造函数中传入
# test = Test(cond="cond value")
# print(test.get_xml_string())
#
# p = Parent()
# print(p.get_xml_string())
#
# # 为builder对象的成员赋值：
# # XMLProperty成员直接赋值字符串
# p.m = "789"
# # ChildBuilder直接赋值自己生成的builder
# # 注意：赋值的builder类型需与声明的保持一致： type(p.t) == type(test)
# p.t2 = Test2()
# print(p.get_xml_string())
# # 可以从父builder直接访问子builder的property，理论上可以无限嵌套
# p.t2.a = "na ni"
# # single 对象直接使用 . 来get,set
# # 非single对象，使用append, get, set函数处理数组
# # 也可以使用[]替代get, set函数
# p.t.get(0).a = "888"
# p.t.set(1, test)
# print(p.get_xml_string())
# print(p.t[0].get_xml_string())
# p.t[0] = Test(cond="teeeeeeee")
# print(p.t[0].get_xml_string())
# #使用”a.b" 语法获取的property 和 childBuilder拿到的是Elementbase类型或string， 使用xml_api中的函数对其操作
#
# p.t.set(1, None)
# p.t.set(0, None)
# print(p.get_xml_string())


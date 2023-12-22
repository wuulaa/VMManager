from src.utils.xml_builder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder


class DomainCpu(XMLBuilder):
    XML_NAME = "cpu"

    mode = XMLProperty("./@mode")
    check = XMLProperty("./@check")

    
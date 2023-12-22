from src.utils.xml_builder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder


class DomainFeatures(XMLBuilder):
    """
    Class for generating <features> XML
    """
    XML_NAME = "features"
    _XML_PROP_ORDER = ["acpi", "apic", "pae", "gic_version"]

    acpi = XMLProperty("./acpi", is_bool=True)
    apic = XMLProperty("./apic", is_bool=True)
    gic = XMLProperty("./gic/@version")
    pae = XMLProperty("./pae", is_bool=True)
    vmport = XMLProperty("./vmport/@state", is_onoff=True)
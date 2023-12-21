from src.domain_xml.device.device import Device
from src.utils.xml_builder.xml_builder import XMLProperty


class DeviceIommu(Device):
    XML_NAME = "iommu"

    model = XMLProperty("./@model")
    aw_bits = XMLProperty("./driver/@aw_bits", is_int=True)
    intremap = XMLProperty("./driver/@intremap", is_onoff=True)
    caching_mode = XMLProperty("./driver/@caching_mode", is_onoff=True)
    eim = XMLProperty("./driver/@eim", is_onoff=True)
    iotlb = XMLProperty("./driver/@iotlb", is_onoff=True)
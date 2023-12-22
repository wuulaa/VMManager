from src.domain_xml.device.device import Device
from src.utils.xml_builder.xml_builder import XMLProperty

class DeviceAudio(Device):
    XML_NAME = "audio"

    type = XMLProperty("./@type")
    id = XMLProperty("./@id")
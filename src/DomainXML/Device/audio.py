from src.DomainXML.Device.device import Device
from src.Utils.XMLBuilder.xml_builder import XMLProperty

class DeviceAudio(Device):
    XML_NAME = "audio"

    type = XMLProperty("./@type")
    id = XMLProperty("./@id")
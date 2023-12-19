from src.DomainXML.Device.device import Device
from src.Utils.XMLBuilder.xml_builder import XMLProperty


class DeviceMemballoon(Device):
    XML_NAME = "memballoon"

    model = XMLProperty("./@model")
    autodeflate = XMLProperty("./@autodeflate", is_onoff=True)
    stats_period = XMLProperty("./stats/@period", is_int=True)
    freePageReporting = XMLProperty("./@freePageReporting", is_onoff=True)


    ##################
    # Default config #
    ##################

    # def set_defaults(self, guest):
    #     if not self.model:
    #         self.model = "virtio"

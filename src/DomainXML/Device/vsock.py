from src.DomainXML.Device.device import Device
from src.Utils.XMLBuilder.xml_builder import XMLProperty


class DeviceVsock(Device):
    XML_NAME = "vsock"

    model = XMLProperty("./@model")
    auto_cid = XMLProperty("./cid/@auto", is_yesno=True)
    cid = XMLProperty("./cid/@address", is_int=True)


    ##################
    # Default config #
    ##################

    # def set_defaults(self, guest):
    #     if not self.model:
    #         self.model = "virtio"
    #
    #     if self.auto_cid is None and self.cid is None:
    #         self.auto_cid = True

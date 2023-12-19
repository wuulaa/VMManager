from src.DomainXML.Device.device import Device
from src.Utils.XMLBuilder.xml_builder import XMLProperty, XMLChildBuilder, XMLBuilder


class _Codec(XMLBuilder):
    """
    Class for generating <sound> child <codec> XML
    """
    XML_NAME = "codec"

    type = XMLProperty("./@type")


class DeviceSound(Device):
    XML_NAME = "sound"

    model = XMLProperty("./@model")
    codecs = XMLChildBuilder(_Codec, is_single=False)
    audio_id = XMLProperty("./audio/@id")


    # ##################
    # # Default config #
    # ##################
    #
    # @staticmethod
    # def default_model(guest):
    #     if guest.defaults_to_pcie():
    #         return "ich9"
    #     return "ich6"
    #
    # def set_defaults(self, guest):
    #     if not self.model:
    #         self.model = self.default_model(guest)

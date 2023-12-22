from src.utils.xml_builder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder
from src.domain_xml.device.device import Device


class DeviceController(Device):
    XML_NAME = "controller"

    TYPE_IDE             = "ide"
    TYPE_FDC             = "fdc"
    TYPE_SCSI            = "scsi"
    TYPE_SATA            = "sata"
    TYPE_VIRTIOSERIAL    = "virtio-serial"
    TYPE_USB             = "usb"
    TYPE_PCI             = "pci"
    TYPE_CCID            = "ccid"
    TYPE_XENBUS          = "xenbus"

    type = XMLProperty("./@type")
    model = XMLProperty("./@model")
    vectors = XMLProperty("./@vectors", is_int=True)
    ports = XMLProperty("./@ports", is_int=True)
    maxGrantFrames = XMLProperty("./@maxGrantFrames", is_int=True)
    index = XMLProperty("./@index")

    driver_iothread = XMLProperty("./driver/@iothread", is_int=True)
    driver_queues = XMLProperty("./driver/@queues", is_int=True)

    master_startport = XMLProperty("./master/@startport", is_int=True)

    target_chassisNr = XMLProperty("./target/@chassisNr", is_int=True)
    target_chassis = XMLProperty("./target/@chassis", is_int=True)
    target_port = XMLProperty("./target/@port", is_int=True)
    target_hotplug = XMLProperty("./target/@hotplug", is_onoff=True)
    target_busNr = XMLProperty("./target/@busNr", is_int=True)
    target_index = XMLProperty("./target/@index", is_int=True)
    target_node = XMLProperty("./target/node", is_int=True)
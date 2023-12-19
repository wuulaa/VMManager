from src.Utils.XMLBuilder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder


class DeviceVirtioDriver(XMLBuilder):
    """
    Represents shared virtio <driver> options
    """
    XML_NAME = "driver"
    ats = XMLProperty("./@ats", is_onoff=True)
    iommu = XMLProperty("./@iommu", is_onoff=True)
    packed = XMLProperty("./@packed", is_onoff=True)
    page_per_vq = XMLProperty("./@page_per_vq", is_onoff=True)


class DeviceSeclabel(XMLBuilder):
    """
    Minimal seclabel that's used for device sources.
    """
    XML_NAME = "seclabel"
    model = XMLProperty("./@model")
    relabel = XMLProperty("./@relabel", is_yesno=True)
    label = XMLProperty("./label")


class DeviceAlias(XMLBuilder):
    XML_NAME = "alias"
    name = XMLProperty("./@name")


class DeviceBoot(XMLBuilder):
    XML_NAME = "boot"
    order = XMLProperty("./@order", is_int=True)
    loadparm = XMLProperty("./@loadparm")


class DeviceAddress(XMLBuilder):
    """
    Examples:
    <address type='pci' domain='0x0000' bus='0x00' slot='0x04' function='0x0'/>
    <address type='drive' controller='0' bus='0' unit='0'/>
    <address type='ccid' controller='0' slot='0'/>
    <address type='virtio-serial' controller='1' bus='0' port='4'/>
    """

    ADDRESS_TYPE_PCI = "pci"
    ADDRESS_TYPE_DRIVE = "drive"
    ADDRESS_TYPE_VIRTIO_SERIAL = "virtio-serial"
    ADDRESS_TYPE_CCID = "ccid"
    ADDRESS_TYPE_SPAPR_VIO = "spapr-vio"

    XML_NAME = "address"

    type = XMLProperty("./@type")

    # type=pci
    domain = XMLProperty("./@domain", is_int=True)
    bus = XMLProperty("./@bus", is_int=True)
    slot = XMLProperty("./@slot", is_int=True)
    function = XMLProperty("./@function", is_int=True)
    multifunction = XMLProperty("./@multifunction", is_onoff=True)
    zpci_uid = XMLProperty("./zpci/@uid")
    zpci_fid = XMLProperty("./zpci/@fid")

    # type=drive
    controller = XMLProperty("./@controller", is_int=True)
    unit = XMLProperty("./@unit", is_int=True)
    port = XMLProperty("./@port", is_int=True)
    target = XMLProperty("./@target", is_int=True)

    # type=spapr-vio
    reg = XMLProperty("./@reg")

    # type=ccw
    cssid = XMLProperty("./@cssid")
    ssid = XMLProperty("./@ssid")
    devno = XMLProperty("./@devno")

    # type=isa
    iobase = XMLProperty("./@iobase")
    irq = XMLProperty("./@irq")

    # type=dimm
    base = XMLProperty("./@base")


class Device(XMLBuilder):
    """
    Base class for all domain xml device objects.
    """
    XML_NAME = "device"

    alias = XMLChildBuilder(DeviceAlias, is_single=True)
    address = XMLChildBuilder(DeviceAddress, is_single=True)
    boot = XMLChildBuilder(DeviceBoot, is_single=True)
    virtio_driver = XMLChildBuilder(DeviceVirtioDriver, is_single=True)

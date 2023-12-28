import random

import libvirt
from src.domain_xml.device.device import Device
from src.utils.xml_builder.xml_builder import XMLProperty, XMLChildBuilder, XMLBuilder


class VirtualPort(XMLBuilder):
    XML_NAME = "virtualport"

    type = XMLProperty("./@type")
    managerid = XMLProperty("./parameters/@managerid", is_int=True)
    typeid = XMLProperty("./parameters/@typeid", is_int=True)
    typeidversion = XMLProperty("./parameters/@typeidversion", is_int=True)
    instanceid = XMLProperty("./parameters/@instanceid")
    profileid = XMLProperty("./parameters/@profileid")
    interfaceid = XMLProperty("./parameters/@interfaceid")


class DeviceInterface(Device):
    XML_NAME = "interface"

    TYPE_BRIDGE = "bridge"
    TYPE_VIRTUAL = "network"
    TYPE_USER = "user"
    TYPE_VHOSTUSER = "vhostuser"
    TYPE_ETHERNET = "ethernet"
    TYPE_DIRECT = "direct"

    ##################
    # XML properties #
    ##################

    bridge = XMLProperty("./source/@bridge")
    network = XMLProperty("./source/@network")
    source_dev = XMLProperty("./source/@dev")

    virtual_port = XMLChildBuilder(VirtualPort, is_single=True)
    type = XMLProperty("./@type")
    trustGuestRxFilters = XMLProperty("./@trustGuestRxFilters", is_yesno=True)

    mac_addr = XMLProperty("./mac/@address")

    source_type = XMLProperty("./source/@type")
    source_path = XMLProperty("./source/@path")
    source_mode = XMLProperty("./source/@mode")
    port_group = XMLProperty("./source/@portgroup")
    model = XMLProperty("./model/@type")
    target_dev = XMLProperty("./target/@dev")
    filter_ref = XMLProperty("./filterref/@filter")
    link_state = XMLProperty("./link/@state")

    driver_name = XMLProperty("./driver/@name")
    driver_queues = XMLProperty("./driver/@queues", is_int=True)

    rom_bar = XMLProperty("./rom/@bar", is_onoff=True)
    rom_file = XMLProperty("./rom/@file")

    mtu_size = XMLProperty("./mtu/@size", is_int=True)


def _random_mac(conn:libvirt.virConnect):
    """Generate a random MAC address.

    00-16-3E allocated to xensource
    52-54-00 used by qemu/kvm
    Different hardware firms have their own unique OUI for mac address.
    The OUI list is available at https://standards.ieee.org/regauth/oui/oui.txt.

    The remaining 3 fields are random, with the first bit of the first
    random field set 0.
    """
    connection_name: str = conn.getURI()
    if connection_name.startswith("qemu"):
        # qemu
        oui = [0x52, 0x54, 0x00]
    else:
        # Xen
        oui = [0x00, 0x16, 0x3E]
    mac = oui + [
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)]
    return ':'.join(["%02x" % x for x in mac])


####################
# Helper Functions #
####################
def create_default_interface_builder(interface_type: str = "network",
                             mac: str = None,
                             source_network: str = "default",
                             model_type: str = "virtio",
                             ) -> DeviceInterface:
    device_interface = DeviceInterface()
    device_interface.type = interface_type
    if mac is not None:
        device_interface.mac_addr = mac
    device_interface.network = source_network
    device_interface.model = model_type
    return device_interface


def create_ovs_interface(ovs_bridge_name: str,
                         mac: str = None):
    device_interface = DeviceInterface()
    device_interface.type = 'bridge'
    device_interface.mac_addr = mac
    device_interface.bridge = ovs_bridge_name

    virtual_port = VirtualPort()
    virtual_port.type = 'openvswitch'

    device_interface.virtual_port = virtual_port
    return device_interface


def create_direct_ovs_interface(ovs_port_name: str,
                                mac: str = None):
    device_interface = DeviceInterface()
    device_interface.type = 'direct'
    device_interface.mac_addr = mac
    device_interface.source_dev = ovs_port_name
    device_interface.source_mode = 'bridge'
    # device_interface.target_dev = 'macvtap0'
    device_interface.model = 'virtio'

    virtual_port = VirtualPort()
    virtual_port.type = 'openvswitch'

    device_interface.virtual_port = virtual_port
    return device_interface


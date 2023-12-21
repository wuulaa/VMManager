"""
This file implements classes for managing libvirt network xml
See https://libvirt.org/formatnetwork.html for details.
A network in libvirt stands for a virtual network switch (vswitch).
See https://wiki.libvirt.org/VirtualNetworking.html for concepts.
"""
from src.utils.xml_builder.xml_builder import XMLProperty, XMLChildBuilder, XMLBuilder


class NetworkDHCPRange(XMLBuilder):
    """
    example:
    <dhcp>
      <range start="192.168.122.128" end="192.168.122.254"/>
    </dhcp>
    """
    XML_NAME = "range"
    start = XMLProperty("./@start")
    end = XMLProperty("./@end")


class NetworkDHCPHost(XMLBuilder):
    """
    example:
    <host mac="00:16:3e:77:e2:ed" name="foo.example.com" ip="192.168.122.10">
    """
    XML_NAME = "host"
    macaddr = XMLProperty("./@mac")
    name = XMLProperty("./@name")
    ip = XMLProperty("./@ip")


class NetworkIP(XMLBuilder):
    """
    example:
    <ip address="192.168.122.1" netmask="255.255.255.0">
         <dhcp>
              <range start="192.168.122.100" end="192.168.122.254" />
              <host mac="00:16:3e:e2:ed" name="foo.example.com" ip="192.168.122.10" />
         </dhcp>
    </ip>
    """
    XML_NAME = "ip"

    family = XMLProperty("./@family")
    address = XMLProperty("./@address")
    prefix = XMLProperty("./@prefix", is_int=True)
    netmask = XMLProperty("./@netmask")

    tftp = XMLProperty("./tftp/@root")
    bootp_file = XMLProperty("./dhcp/bootp/@file")
    bootp_server = XMLProperty("./dhcp/bootp/@server")

    ranges = XMLChildBuilder(NetworkDHCPRange, relative_xpath="./dhcp", is_single=False)
    hosts = XMLChildBuilder(NetworkDHCPHost, relative_xpath="./dhcp", is_single=False)


class NetworkRoute(XMLBuilder):
    """
    example:
    <route family="ipv6" address="2001:db8:ca2:3::" prefix="64" gateway="2001:db8:ca2:2::2"/>
    """
    XML_NAME = "route"

    family = XMLProperty("./@family")
    address = XMLProperty("./@address")
    prefix = XMLProperty("./@prefix", is_int=True)
    gateway = XMLProperty("./@gateway")
    netmask = XMLProperty("./@netmask")


class NetworkForwardPf(XMLBuilder):
    """
    example:
    <pf dev='eth0'/>
    """
    XML_NAME = "pf"
    dev = XMLProperty("./@dev")


class NetworkForward(XMLBuilder):
    """
    example:
    <forward mode='hostdev' managed='yes'>
        <driver name='vfio'/>
        <address type='pci' domain='0' bus='4' slot='0' function='1'/>
        <address type='pci' domain='0' bus='4' slot='0' function='2'/>
        <address type='pci' domain='0' bus='4' slot='0' function='3'/>
    </forward>
    """
    XML_NAME = "forward"

    mode = XMLProperty("./@mode")
    dev = XMLProperty("./@dev")
    managed = XMLProperty("./@managed")
    pf = XMLChildBuilder(NetworkForwardPf)


class NetworkPortgroup(XMLBuilder):
    """
    example:
    <portgroup name='dontpanic'>
        <vlan>
          <tag id='42'/>
        </vlan>
    </portgroup>
    """
    XML_NAME = "portgroup"

    name = XMLProperty("./@name")
    default = XMLProperty("./@default", is_yesno=True)


class Network(XMLBuilder):
    """
    Top level class for <network> object XML
    """
    XML_NAME = "network"
    # _XML_PROP_ORDER = ["ipv6", "name", "uuid", "forward", "virtualport_type",
    #                    "bridge", "stp", "delay", "domain_name",
    #                    "macaddr", "ips", "routes"]

    ipv6 = XMLProperty("./@ipv6", is_yesno=True)
    name = XMLProperty("./name")
    uuid = XMLProperty("./uuid")

    virtualport_type = XMLProperty("./virtualport/@type")

    # Not entirely correct, there can be multiple routes
    forward = XMLChildBuilder(NetworkForward, is_single=True)

    domain_name = XMLProperty("./domain/@name")

    bridge = XMLProperty("./bridge/@name")
    stp = XMLProperty("./bridge/@stp", is_onoff=True)
    delay = XMLProperty("./bridge/@delay", is_int=True)
    macaddr = XMLProperty("./mac/@address")

    portgroups = XMLChildBuilder(NetworkPortgroup, is_single=False)
    ips = XMLChildBuilder(NetworkIP, is_single=False)
    routes = XMLChildBuilder(NetworkRoute, is_single=False)


####################
# Helper Functions #
####################
def create_network_xml_builder(name: str,
                       ip_address: str,
                       ip_netmask: str,
                       uuid: str = None,
                       mode: str = None,
                       dev: str = None,
                       bridge_name: str = None,
                       ) -> Network:
    network = Network()
    network.name = name
    network.uuid = uuid
    network.bridge = bridge_name
    ip = NetworkIP()
    ip.address = ip_address
    ip.netmask = ip_netmask
    network.ips.append(ip)

    if mode is not None or dev is not None:
        forward = NetworkForward()
        forward.mode = mode
        forward.dev = dev
        network.forward = forward

    return network


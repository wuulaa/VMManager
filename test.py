# import libvirt
import random
# name = "template1"
# conn = libvirt.open("qemu:///system")

# domain = conn.lookupByName(name)
# # domain.interfaceAddresses()
# # domain.interfaceStats("default")
# interfaces = conn.listAllInterfaces()
# for interface in interfaces:
#     print(interface.name())
#     print(interface.MACString())
# ifaces = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
# print(ifaces)

def random_mac():
    """Generate a random MAC address.

    00-16-3E allocated to xensource
    52-54-00 used by qemu/kvm
    Different hardware firms have their own unique OUI for mac address.
    The OUI list is available at https://standards.ieee.org/regauth/oui/oui.txt.

    The remaining 3 fields are random, with the first bit of the first
    random field set 0.
    """
    oui = [0x52, 0x54, 0x00]
    mac = oui + [
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff),
        random.randint(0x00, 0xff)]
    return ':'.join(["%02x" % x for x in mac])
print(random_mac())




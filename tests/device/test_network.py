import sys
import libvirt
import src.device.network as nw
import src.manage.network_manager as nm
print(sys.path)
conn = libvirt.open("qemu:///system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")

domains = conn.listAllDomains()

domain = domains[0]


def test_network_xml():
    network = nw.create_network_xml_builder("test",
                                            ip_address="192.168.11.11",
                                            ip_netmask="255.255.255.0",
                                            mode="nat")
    print(network.get_xml_string())
    res = nm.define_network(conn, network.get_xml_string())
    assert res is not None


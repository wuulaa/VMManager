import sys
import libvirt
import src.manage.device_manager as dm
import src.device.interface as interface
print(sys.path)
conn = libvirt.open("qemu:///system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")

domains = conn.listAllDomains()

domain = domains[0]


def test_set_domain_name():
    name_index = 0
    old_name = domain.name()
    new_name = "centos" + str(name_index)
    while old_name == new_name:
        name_index = name_index + 1
        new_name = "centos" + str(name_index)

    res = dm.set_domain_name(domain, new_name)
    assert (res.get("is_success") == True) and (domain.name() == new_name)


def test_set_domain_title_and_description():
    old_description = domain.metadata(libvirt.VIR_DOMAIN_METADATA_DESCRIPTION, None)
    description = old_description + "des "
    res1 = dm.set_domain_description(domain,description)
    old_title = domain.metadata(libvirt.VIR_DOMAIN_METADATA_TITLE, None)
    title = old_title + "title "
    res2 = dm.set_domain_title(domain, title)
    assert (res1.get("is_success") == True) and (res2.get("is_success") == True)


def test_set_domain_cpu():
    old_cpu_num = domain.vcpusFlags()
    res = dm.set_domain_vcpu(domain, old_cpu_num + 1)
    assert res.get("is_success") == True


def test_set_domain_memory():
    res = dm.set_domain_memory(domain, 1024*1024*2)
    assert res.get("is_success") == True


def test_attach_device():
    network = '''<interface type="network">
        <source network="default"/>
        <mac address="52:54:00:57:40:c5"/>
        <model type="virtio"/>
        <alias name="net8"/>
    </interface>'''
    res = dm.attach_device_to_domain(domain, network)
    assert res.get("is_success") == True


def test_detach_device():
    network = '''<interface type="network">
        <source network="default"/>
        <mac address="52:54:00:57:40:c5"/>
        <model type="virtio"/>
    </interface>'''
    res = dm.detach_device_from_domain(domain, network)
    assert res.get("is_success") == True

def test_update_device():
    network = '''<interface type="network">
        <source network="default"/>
        <mac address="52:54:00:57:40:c5"/>
        <model type="virtio"/>
    </interface>'''
    res = dm.detach_device_from_domain(domain, network)
    assert res.get("is_success") == True


def test_interface_xml():
    interface_builder = interface.create_interface_builder()
    print(interface_builder.get_xml_string())
    res = dm.attach_device_to_domain(domain, interface_builder.get_xml_string())
    assert res.get("is_success") == True


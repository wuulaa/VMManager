import libvirt
from utils.response import APIResponse


def list_all_network(conn: libvirt.virConnect):
    nets = conn.listAllNetworks()
    return APIResponse.success(nets)


def create_network(conn: libvirt.virConnect, xml: str):
    try: 
        network = conn.networkCreateXML(xml)
        return APIResponse.success(network)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


def define_network(conn: libvirt.virConnect, xml: str):
    try: 
        network = conn.networkDefineXML(xml)
        return APIResponse.success(network)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


def start_network(conn: libvirt.virConnect, network: libvirt.virNetwork):
    try:
        network.create()
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


def stop_network(conn: libvirt.virConnect, network: libvirt.virNetwork):
    try:
        network.undefine()
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


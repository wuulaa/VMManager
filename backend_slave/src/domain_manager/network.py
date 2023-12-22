import libvirt

def list_all_network(conn: libvirt.virConnect) -> list:
    return conn.listAllNetworks()


def create_network(conn: libvirt.virConnect, xml: str) -> libvirt.virNetwork:
    return conn.networkCreateXML(xml)


def define_network(conn: libvirt.virConnect, xml: str) -> libvirt.virNetwork:
    return conn.networkDefineXML(xml)


def start_network(network: libvirt.virNetwork):
    try:
        network.create()
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


def stop_network(network: libvirt.virNetwork):
    try:
        network.undefine()
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


import libvirt
from utils.response import APIResponse

error_info = {
    400:"Unkown exception.",
    401:"Count Exceeds limit",
    404:"VM not found."
    
}

def list_all_network(conn: libvirt.virConnect):
    nets = conn.listAllNetworks()
    return APIResponse.success(nets)


def look_up_network_by_name(conn: libvirt.virConnect, name: str):
    network: libvirt.virNetwork = conn.networkLookupByName(name)
    return APIResponse.success(data=network)


def look_up_network_by_UUID(conn: libvirt.virConnect, uuid: str):
    network: libvirt.virNetwork = conn.networkLookupByUUIDString(uuid)
    return APIResponse.success(data=network)


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



def undefine_network(conn: libvirt.virConnect, network_uuid: str):
    try:
        network = conn.networkLookupByUUIDString(network_uuid)
        if network is None:
            return APIResponse.error(404, error_info.get(404))
        
        network.undefine()
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


def start_network(conn: libvirt.virConnect, network_uuid: str):
    try:
        network = conn.networkLookupByUUIDString(network_uuid)
        if network is None:
            return APIResponse.error(404, error_info.get(404))
        network.create()
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


def destroy_network(conn: libvirt.virConnect, network_uuid: str):
    try:
        network = conn.networkLookupByUUIDString(network_uuid)
        if network is None:
            return APIResponse.error(404, error_info.get(404))
        network.destroy()
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


def set_network_auto_start(conn: libvirt.virConnect, network_uuid: str, autostart: bool):
    try:
        network = conn.networkLookupByUUIDString(network_uuid)
        if network is None:
            return APIResponse.error(404, error_info.get(404))
        network.setAutostart(autostart)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))


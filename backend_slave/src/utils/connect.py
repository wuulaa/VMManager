import libvirt
from src.utils import consts

def get_libvirt_connection() -> libvirt.virConnect:
    conn = None
    try:
        conn = libvirt.open(consts.QEMU_CONN)
    except libvirt.libvirtError:
        print("Failed to open connection to qemu:///system")
    return conn

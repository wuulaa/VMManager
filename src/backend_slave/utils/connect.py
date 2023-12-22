import libvirt


def get_libvirt_connection() -> libvirt.virConnect:
    conn = None
    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError:
        print("Failed to open connection to qemu:///system")
    return conn


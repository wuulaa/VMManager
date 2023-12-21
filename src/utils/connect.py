import libvirt


def get_connected(User):
    try:
        conn = libvirt.open('qemu+ssh://' + User + '/system') 
    except libvirt.libvirtError:
        print('Failed to open connection to qemu+ssh://'+User+'/system')
        return None
    else:
        print('Connection to qemu+ssh://'+User+'/system succeeded')
        return conn


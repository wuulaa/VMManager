from src.utils import config

CONF = config.CONF

class RbdSettings(object):
    # module
    pool_driver = 'src.volume.driver.pool.rbd_pool.RbdPool'
    volume_driver = 'src.volume.driver.volume.rbd_volume.RbdVolume'
    xml_builder = 'src.volume.xml.volume.rbd_builder.RbdVolumeXMLBuilder'


class LibvirtSettings(object):
    # module
    pool_driver = 'src.volume.driver.pool.libvirt_pool.LibvirtPool'
    volume_driver = 'src.volume.driver.volume.libvirt_volume.LibvirtVolume'
    xml_builder = 'src.volume.xml.volume.libvirt_builder.LibvirtVolumeXMLBuilder'

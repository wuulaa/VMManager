from oslo_config import cfg

CONF = cfg.CONF
CONF(default_config_files=['src/volume/common/volume.conf'])

# 定义配置项
provider_opts = [
    cfg.StrOpt('provider', default='rbd',
               help='Specify the volume provider'),
]

rbd_options = [
    cfg.StrOpt('pool_driver',
               default='src.volume.driver.pool.rbd_pool.RbdPool',
               help='Specify the pool driver'),
    cfg.StrOpt('volume_driver',
               default='src.volume.driver.volume.rbd_volume.RbdVolume',
               help='Specify the volume driver'),
    cfg.StrOpt('xml_builder',
               default='src.volume.xml.volume.rbd_builder.RbdVolumeXMLBuilder',
               help='Specify the xml builder'),
    cfg.StrOpt('pool_name',
               default='volume-pool',
               help='Name of ceph rbd pool'),
    cfg.StrOpt('host_name',
               default='kunpeng',
               help='Name of this node'),
    cfg.StrOpt('host_port',
               default='6789',
               help='Port to access rbd service'),
    cfg.StrOpt('auth_user',
               default='libvirt',
               help='Name of ceph user to access rbd service'),
    cfg.StrOpt('secret_uuid',
               default='250541ca-7b24-4afb-b185-4f50f1606635',
               help='UUID of the secret to store ceph user key'),
]
libvirt_options = [
    cfg.StrOpt('pool_driver',
               default='src.volume.driver.pool.libvirt_pool.LibvirtPool',
               help='Specify the pool driver'),
    cfg.StrOpt('volume_driver',
               default='src.volume.driver.volume.libvirt_volume.LibvirtVolume',
               help='Specify the volume driver'),
    cfg.StrOpt('xml_builder',
               default='src.volume.xml.volume.libvirt_builder.LibvirtVolumeXMLBuilder',
               help='Specify the xml builder')
]

CONF.register_opts(provider_opts)
CONF.register_opts(libvirt_options, 'libvirt')
CONF.register_opts(rbd_options, 'rbd')

from .volume_builder import VolumeXMLBuilder
from src.DomainXML.Device.common import Auth, Host
from src.DomainXML.Device.disk import DeviceDisk, DiskSource
from src.Utils.singleton import singleton
from src.Volume.common import config


CONF = config.CONF

POOL_NAME = CONF.rbd.pool_name
HOST_NAME = CONF.rbd.host_name
HOST_PORT = CONF.rbd.host_port
AUTH_USER = CONF.rbd.auth_user
SECRET_UUID = CONF.rbd.secret_uuid


@singleton
class RbdVolumeXMLBuilder(VolumeXMLBuilder):

    KEY_WORD = ['volume_name',
                'dev_order']

    def _build_auth(self, **kwargs):
        auth = Auth()
        auth.username = AUTH_USER
        auth.secret_type = 'ceph'
        auth.secret_uuid = SECRET_UUID
        self._disk.auth = auth

    def _build_disk(self, **kwargs):
        self._disk = DeviceDisk()
        self._disk.type = 'network'
        self._disk.device = 'disk'

        # driver
        self._disk.driver_name = 'qemu'
        self._disk.driver_type = 'raw'

        # target
        _dev_order = chr(97 + kwargs.get("dev_order"))
        self._disk.target_dev = f'vd{_dev_order}'   # 'a' + order
        self._disk.target_bus = 'virtio'

    def _build_source(self, **kwargs):
        host = Host()
        host.name = HOST_NAME
        host.port = HOST_PORT

        source = DiskSource()
        source.protocol = 'rbd'
        source.name = f'{POOL_NAME}/{kwargs.get("volume_name")}'
        source.host = host

        self._disk.source = source

    def construct(self,
                  volume_name: str = None,
                  dev_order: int = 0) -> DeviceDisk:
        return super().construct(volume_name=volume_name,
                                 dev_order=dev_order)


# disk = RbdVolumeXMLBuilder().construct(volume_name='test-image',
#                                        dev_order=0)

# print(disk.get_xml_string())

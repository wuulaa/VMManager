import pytest
import datetime
from importlib import reload
from unittest import mock
from src.DomainXML.Device.disk import DeviceDisk
from src.Utils.response import APIResponse
from src.Volume.db.models import Pool
from src.Volume.service import volume as volume_service
from src.Volume.service.volume import VolumeService


volume_list = {
    'libvirt-pool/test-image': {
        'pool_id': '4e1e6ea0-3b3f-4b66-8670-09c0558de5d0',
        'volume_name': 'test-image',
        'allocation': '20480'
    },

    'libvirt-pool/rbd-image': {
        'pool_id': '4e1e6ea0-3b3f-4b66-8670-09c0558de5d0',
        'volume_name': 'rbd-image',
        'allocation': '51200'
    },
}


class TestVolumeService():

    service = VolumeService()

    @pytest.fixture
    def pool(self):
        pool = Pool(name='libvirt-pool',
                    allocation='102400',
                    owner='Sonya')
        pool.id = '4e1e6ea0-3b3f-4b66-8670-09c0558de5d0'
        pool.status = 0
        pool.deleted_at = None
        pool.deleted = 0
        pool.created_at = datetime.datetime(2023, 11, 14, 9, 42, 36)
        pool.update_at = None
        return pool

    @pytest.mark.parametrize('dict', list(volume_list.values()), ids=list(volume_list.keys()))
    # mock CONF.provider
    @mock.patch.object(volume_service.CONF, 'provider', 'rbd')
    @mock.patch('src.Volume.service.volume.db.insert')
    @mock.patch('src.Volume.service.volume.volume_driver.create')
    @mock.patch('src.Volume.service.volume.db.select_by_id')
    def test_create_rbd_volume(self, mock_query, mock_create, mock_insert, dict, pool):
        reload(volume_service)   # reload volume_module and volume_driver

        mock_query.return_value = pool
        mock_create.return_value = APIResponse.success()
        volume = self.service.create_volume(dict['pool_id'],
                                            dict['volume_name'],
                                            dict['allocation'])
        mock_query.assert_called_once()
        mock_create.assert_called_once()
        mock_insert.assert_called_once()
        assert volume_service.CONF.provider == 'rbd'
        assert volume_service.volume_driver_path == 'src.Volume.driver.volume.rbd_volume.RbdVolume'

        RBD_CONF = volume_service.CONF.rbd
        disk = volume._get_device()
        assert disk.type == 'network'
        assert disk.device == 'disk'
        assert disk.driver_name == 'qemu'
        assert disk.driver_type == 'raw'
        assert disk.source.protocol == 'rbd'
        assert disk.source.name == f'{RBD_CONF.pool_name}/{dict["volume_name"]}'
        assert disk.source.host.name == RBD_CONF.host_name
        assert disk.source.host.port == RBD_CONF.host_port
        assert disk.auth.username == RBD_CONF.auth_user
        assert disk.auth.secret_type == 'ceph'
        assert disk.auth.secret_uuid == RBD_CONF.secret_uuid
        assert disk.target_dev == 'vda'
        assert disk.target_bus == 'virtio'

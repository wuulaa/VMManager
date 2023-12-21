import pytest
from src.volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder


rbd_list = {
    'libvirt-pool/test-image': {
        'host_name': 'kunpeng',
        'host_port': '6789',
        'source_name': 'libvirt-pool/test-image',
        'auth_username': 'libvirt',
        'secret_uuid': 'f60f4ce7-d260-448b-aede-ad5110d27a17',
        'target_dev': 'vda'
    },

    'libvirt-pool/test2': {
        'host_name': 'ceph1',
        'host_port': '67890',
        'source_name': 'libvirt-pool/test2',
        'auth_username': 'volume_manager',
        'secret_uuid': 'abcdefgh-d260-448b-aede-ad5110d27a17',
        'target_dev': 'vde'
    },
}


@pytest.mark.parametrize('dict',
                         list(rbd_list.values()),
                         ids=list(rbd_list.keys()))
def test_rbd_volume_xml_builder_construct(dict):
    disk = RbdVolumeXMLBuilder().construct(host_name=dict['host_name'],
                                           host_port=dict['host_port'],
                                           source_name=dict['source_name'],
                                           auth_username=dict['auth_username'],
                                           secret_uuid=dict['secret_uuid'],
                                           dev_order=dict['target_dev'])
    assert disk.type == 'network'
    assert disk.device == 'disk'
    assert disk.driver_name == 'qemu'
    assert disk.driver_type == 'raw'
    assert disk.source.protocol == 'rbd'
    assert disk.source.name == dict['source_name']
    assert disk.source.host.name == dict['host_name']
    assert disk.source.host.port == dict['host_port']
    assert disk.auth.username == dict['auth_username']
    assert disk.auth.secret_type == 'ceph'
    assert disk.auth.secret_uuid == dict['secret_uuid']
    assert disk.target_dev == dict['target_dev']
    assert disk.target_bus == 'virtio'

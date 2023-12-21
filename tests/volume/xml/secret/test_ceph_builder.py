import pytest
from src.volume.xml.secret.ceph_builder import CephSecretXMLBuilder


@pytest.mark.parametrize('secret_uuid',
                         ['2d621bf7-8a9a-4aa7-a5ec-b55311939c54',
                          '250541ca-7b24-4afb-b185-4f50f1606635'],
                         ids=['kunpeng', 'ceph1'])
def test_ceph_secret_xml_builder_construct(secret_uuid):
    secret = CephSecretXMLBuilder().construct(secret_uuid=secret_uuid)

    assert secret.ephemeral is False
    assert secret.private is False
    assert secret.description is None
    assert secret.uuid.text == secret_uuid
    assert secret.usage.volume is None
    assert secret.usage.target is None
    assert secret.usage.type == 'ceph'
    assert secret.usage.name.text == 'ceph backend secret'

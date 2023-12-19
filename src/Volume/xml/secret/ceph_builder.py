from src.Volume.xml.secret.secret_builder import SecretXMLBuilder
from src.Utils.secret import Secret, Usage
from src.Utils.singleton import singleton


@singleton
class CephSecretXMLBuilder(SecretXMLBuilder):

    KEY_WORD = ['secret_uuid']

    def _build_secret(self, **kwargs):
        self._secret = Secret()
        self._secret.private = 'no'
        self._secret.uuid = kwargs.get('secret_uuid')

    def _build_usage(self, **kwargs):
        usage = Usage()
        usage.type = 'ceph'
        usage.name = 'ceph backend secret'
        self._secret.usage = usage

    def construct(self, secret_uuid: str = None) -> Secret:
        return super().construct(secret_uuid=secret_uuid)


secret = CephSecretXMLBuilder().construct(secret_uuid='fe860da6-376e-4a68-9266-3e89cef75f84')
print(secret.get_xml_string())
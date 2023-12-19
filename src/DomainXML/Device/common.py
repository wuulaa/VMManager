from src.Utils.XMLBuilder.xml_builder import XMLBuilder, XMLProperty


class Auth(XMLBuilder):
    """
    <auth username='libvirt'>
        <secret type='ceph' uuid='574d008d-a052-4b03-af27-2beb67462bcf'/>
    </auth>
    """
    XML_NAME = 'auth'
    username = XMLProperty('./@username')

    # secret
    secret_type = XMLProperty('./secret/@type')
    secret_uuid = XMLProperty('./secret/@uuid')


class Target(XMLBuilder):
    XML_NAME = 'target'

    dev = XMLProperty('./@dev')
    bus = XMLProperty('./@bus')
    tray = XMLProperty('./@tray')
    rotation_rate = XMLProperty('./@rotation_rate')


class Host(XMLBuilder):
    """
    example:
    <host name="ceph1" port="6789"/>
    """
    XML_NAME = 'host'
    name = XMLProperty('./@name')
    port = XMLProperty('./@port')

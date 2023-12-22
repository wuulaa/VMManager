from src.utils.xml_builder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder


class Cookies(XMLBuilder):
    XML_NAME = 'cookies'
    value = ('./cookie')
    name = XMLProperty('./cookie/name')

    def create(self, property: dict):
        self.value = property.get("value")
        self.name = property.get("name")


class DeviceCdrom(XMLBuilder):
    # disk: type, device
    XML_NAME = 'disk'
    type = XMLProperty('./@type')
    device = XMLProperty('./@device')

    # driver
    driver_name = XMLProperty('./driver/@name')
    driver_type = XMLProperty('./driver/@type')

    # target
    target_dev = XMLProperty('./target/@dev')
    target_bus = XMLProperty('./target/@bus')
    target_tray = XMLProperty('./target/@tray')
    target_rotation_rate = XMLProperty('./target/@rotation_rate')

    # readonly
    readonly = XMLProperty('./readonly')

    # source
    source_protocol = XMLProperty('./source/@protocol')
    source_name = XMLProperty('./source/@name')
    source_query = XMLProperty('./source/@query')
    source_baz = XMLProperty('./source/@baz')

    # source_host
    source_host_name = XMLProperty('./source/host/@name')
    source_host_port = XMLProperty('./source/host/@port')

    # source_cookies
    cookie = XMLChildBuilder(Cookies)

    # source_readahead
    source_readahead_size = XMLProperty('./source/readahead/@size')

    # source_timeout
    source_timeout_seconds = XMLProperty('./source/timeout/@seconds')

    # source_ssl
    source_ssl = XMLProperty('./source/ssl/@verify')

    def create(self, property: dict):
        self.type = property.get("type")
        self.device = property.get("device")

        self.driver_name = property.get("driver_name")
        self.driver_type = property.get("driver_type")

        self.target_dev = property.get("target_dev")
        self.target_bus = property.get("target_bus")
        self.target_tray = property.get("target_tray")
        self.target_rotation_rate = property.get("target_rotation_rate")

        self.readonly = property.get("readonly")

        self.source_protocol = property.get("source_protocol")
        self.source_name = property.get("source_name")
        self.source_query = property.get("source_query")
        self.source_baz = property.get("source_baz")

        self.source_host_name = property.get("source_host_name")
        self.source_host_port = property.get("source_host_port")

        self.source_readahead_size = property.get("source_readahead_size")

        self.source_timeout_seconds = property.get("source_timeout_seconds")

        self.source_ssl = property.get("source_ssl")


# rom = Cdrom()
# rom.type = 'network'
# rom.device = 'cdrom'
# rom.driver_name = 'qemu'
# rom.driver_type = 'raw'
# rom.source_protocol = 'ftps'
# rom.source_host_name = 'hostname'

# print(rom.get_xml_string())

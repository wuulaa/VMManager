from src.domain_xml.device.device import Device
from src.utils.xml_builder.xml_builder import XMLProperty, XMLChildBuilder, XMLBuilder


class GraphicsListen(XMLBuilder):
    XML_NAME = "listen"

    type = XMLProperty("./@type")
    address = XMLProperty("./@address")
    network = XMLProperty("./@network")
    socket = XMLProperty("./@socket")


class DeviceGraphics(Device):
    XML_NAME = "graphics"

    TYPE_SDL = "sdl"
    TYPE_VNC = "vnc"
    TYPE_RDP = "rdp"
    TYPE_SPICE = "spice"

    # _XML_PROP_ORDER = ["type", "gl", "_port", "_tlsPort", "autoport", "websocket",
    #                    "keymap", "_listen",
    #                    "passwd", "display", "xauth"]

    keymap = XMLProperty("./@keymap")
    port = XMLProperty("./@port", is_int=True)
    tlsPort = XMLProperty("./@tlsPort", is_int=True)

    autoport = XMLProperty("./@autoport", is_yesno=True)
    websocket = XMLProperty("./@websocket", is_int=True)

    xauth = XMLProperty("./@xauth")
    display = XMLProperty("./@display")

    listen = XMLProperty("./@listen")

    type = XMLProperty("./@type")
    passwd = XMLProperty("./@passwd")
    passwdValidTo = XMLProperty("./@passwdValidTo")
    socket = XMLProperty("./@socket")
    connected = XMLProperty("./@connected")
    defaultMode = XMLProperty("./@defaultMode")

    listens = XMLChildBuilder(GraphicsListen, is_single=False)



    # Spice bits
    image_compression = XMLProperty("./image/@compression")
    streaming_mode = XMLProperty("./streaming/@mode")
    clipboard_copypaste = XMLProperty("./clipboard/@copypaste", is_yesno=True)
    mouse_mode = XMLProperty("./mouse/@mode")
    filetransfer_enable = XMLProperty("./filetransfer/@enable", is_yesno=True)
    gl = XMLProperty("./gl/@enable", is_yesno=True)
    rendernode = XMLProperty("./gl/@rendernode")
    zlib_compression = XMLProperty("./zlib/@compression")


    ##################
    # Default config #
    ##################
def create_local_auto_port_spice_viewer():
    """create a local only spice with passwd,
    so no one outside can connect.
    Set address to 0.0.0.0 with user passwd and port if add-spice is called

    """
    
    graphic = DeviceGraphics()
    graphic.type = "spice"
    graphic.port = -1
    graphic.autoport = True
    graphic.listen = "127.0.0.1"
    graphic.passwd = "locked"
    listen = GraphicsListen()
    listen.type = "address"
    listen.address = "127.0.0.1"

    graphic.listens.append(listen)
    graphic.image_compression = "off"
    return graphic    


def create_local_auto_port_vnc_viewer():
    """create a local only spice with passwd,
    so no one outside can connect.
    Set address to 0.0.0.0 with user passwd and port if add-vnc is called

    """
    graphic = DeviceGraphics()
    graphic.type = "vnc"
    graphic.port = -1
    graphic.autoport = True
    graphic.listen = "127.0.0.1"
    graphic.passwd = "locked"
    listen = GraphicsListen()
    listen.type = "address"
    listen.address = "127.0.0.1"

    graphic.listens.append(listen)
    return graphic   


def create_spice_viewer(port: int = None, passwd: str =None):
    graphic = DeviceGraphics()
    graphic.type = "spice"
    if port is None:
        graphic.autoport = True
    else:
        graphic.port = port
        graphic.autoport = False
    graphic.listen = "0.0.0.0"
    if passwd :
        graphic.passwd = passwd
    listen = GraphicsListen()
    listen.type = "address"
    listen.address = "0.0.0.0"

    graphic.listens.append(listen)
    graphic.image_compression = "off"
    return graphic


def create_vnc_viewer(port: int = None, passwd: str = None):
    graphic = DeviceGraphics()
    graphic.type = "vnc"
    if port is None:
        graphic.port = -1
        graphic.autoport = True
    else:
        graphic.port = port
        graphic.autoport = False
    graphic.listen = "0.0.0.0"
    if passwd :
        graphic.passwd = passwd
    listen = GraphicsListen()
    listen.type = "address"
    listen.address = "0.0.0.0"

    graphic.listens.append(listen)
    return graphic


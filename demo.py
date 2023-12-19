import pdb
from src.Utils.XMLBuilder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder
from src.DomainXML.Domain.domainOs import DomainOs, BootDevice
from src.DomainXML.Domain.features import DomainFeatures
from src.DomainXML.Domain.cpu import DomainCpu
from src.DomainXML.Domain.clock import DomainClock
from src.DomainXML.Domain.pm import DomainPm
from src.DomainXML.Device.device import Device
from src.DomainXML.Device.disk import DeviceDisk, create_cdrom_builder, create_disk_builder
from src.DomainXML.Device.cdrom import DeviceCdrom
from src.DomainXML.Device.controller import DeviceController
from src.DomainXML.Device.interface import create_direct_ovs_interface, create_interface_builder, DeviceInterface
from src.DomainXML.Device.char import DeviceSerial, DeviceConsole, CharSource, DeviceChannel
from src.DomainXML.Device.graphics import create_vnc_viewer
from src.DomainXML.Device.input import DeviceInput
from src.DomainXML.Domain.guest import Guest, DomainDevices
from src.Volume.service.volume import VolumeService
from src.Image.Snapshot.snapshot import SnapShot

from src.Network.idl.ovs_lib import OVSDBHelper, OVSBridge, BaseOVS
import src.DomainManager.guest as guest_manager
from src.Volume.xml.volume.rbd_builder import RbdVolumeXMLBuilder
import libvirt
import datetime


# 创建VM存储池
# def create_pool(pool_name: str):
#     pool_service: PoolService = PoolService()
#     if pool_service.get_pool_by_name(pool_name) is not None:
#         return pool_service.get_pool_by_name(pool_name).id
#     pool = pool_service.create_pool(pool_name, allocation=50 * 1024, owner="york")
#     return pool


# # 创建ceph数据卷
# def create_volume(pool_name: str, vol_name: str):
#     pool_id = create_pool(pool_name)
#     print(pool_id)
#     volume_service: VolumeService = VolumeService()
#     volume = volume_service.create_volume(pool_id=pool_id, volume_name=vol_name, allocation=20 * 1024)
#     return volume


# 创建ovs网桥与网卡，提供给虚拟机使用
def create_interfaces(bridge_name: str="demoBridge", port_name: str="demo1"):
    ovs_bridge = None
    ovsdb_helper = OVSDBHelper()
    baseOVS = BaseOVS(ovsdb_helper.ovsIdl)

    # add ovs bridge
    if baseOVS.bridge_exists(bridge_name):
        baseOVS.delete_bridge(bridge_name)
    ovs_bridge = baseOVS.add_bridge(bridge_name)

    # add virtual port to ovs bridge
    if ovs_bridge.port_exists(port_name):
        ovs_bridge.delete_port(port_name)
    ovs_bridge.add_port(port_name, ("type", "internal"))

    # create the interface xml
    default_xml_builder = create_interface_builder()
    ovs_xml_builder = create_direct_ovs_interface(port_name)
    return default_xml_builder, ovs_xml_builder


# 创建domain xml
def create_domain(domain_name):
    guest = Guest()

    # set guest basic values
    guest.domain_name = domain_name
    guest.type = "kvm"
    guest.memoryUnit = "KiB"
    guest.memory = 1048576
    guest.currentMemory = 1048576
    guest.vcpus = 2
    guest.vcpu_placement = "static"

    # set os related values
    domainOS = DomainOs.create_default_os_builder(guest.domain_name)

    # add two boot devices
    bootDevice = BootDevice()
    bootDevice.dev = "cdrom"
    bootDevice2 = BootDevice()
    bootDevice2.dev = "hd"
    domainOS.bootdevs.append(bootDevice)
    domainOS.bootdevs.append(bootDevice2)

    guest.os = domainOS

    # set domain features
    domainFeatures = DomainFeatures()
    domainFeatures.acpi = ''
    domainFeatures.gic = '3'
    guest.features = domainFeatures

    # set domain cpu configs
    cpu = DomainCpu()
    cpu.mode = "host-passthrough"
    cpu.check = "none"
    guest.cpu = cpu

    guest.on_poweroff = "destroy"
    guest.on_reboot = "restart"
    guest.on_crash = "destroy"


    #### Devices ######
    devices = DomainDevices()


    # controller
    scsi_controller = DeviceController()
    scsi_controller.type = 'scsi'
    scsi_controller.index = '0'
    scsi_controller.model = 'virtio-scsi'

    usb_controller = DeviceController()
    usb_controller.type = 'usb'
    usb_controller.index = "0"
    usb_controller.model = "qemu-xhci"
    usb_controller.ports = "15"

    devices.controller.append(scsi_controller)
    devices.controller.append(usb_controller)

    # input
    mouse = DeviceInput()
    mouse.type = "mouse"
    mouse.bus = "usb"

    keyboard = DeviceInput()
    keyboard.type = "keyboard"
    keyboard.bus = "usb"
    devices.input.append(mouse)
    devices.input.append(keyboard)

    # network interfaces
    interface0, interface1 = create_interfaces("demoBridge", domain_name)
    devices.interface.append(interface0)
    devices.interface.append(interface1)
    guest.devices = devices

    # VNC
    vnc_viewer = create_vnc_viewer(15910)
    devices.graphics.append(vnc_viewer)

    # serial
    char_source = CharSource()
    char_source.path = '/dev/pts/2'

    serial = DeviceSerial()
    serial.type = 'pty'
    serial.target_type = 'system-serial'
    serial.target_port = '0'
    serial.target_model_name = 'pl011'
    serial.source = char_source

    # console
    console_source = CharSource()
    console_source.path = '/dev/pts/2'

    console = DeviceConsole()
    console.type = 'pty'
    console.tty = '/dev/pts/2'
    console.target_type = 'serial'
    console.target_port = '0'
    console.source = console_source

    devices.serial.append(serial)
    devices.console.append(console)

    # qemu-channel
    channel = DeviceChannel()
    channel.type = 'unix'
    channel.target_type = "virtio"
    channel.target_name = "org.qemu.guest_agent.0"
    devices.channel.append(channel)

    guest.emulator = "/usr/bin/qemu-system-aarch64"
    print(guest.get_xml_string())
    return guest




conn = libvirt.open("qemu:///system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")

time1 = datetime.datetime.now()

## ************modify this parameter********** ##
domain_name = "domain16"

snap = SnapShot("libvirt-pool", "rbd-with-net")
snap.clone_snap("rbd-with-net", "libvirt-pool", domain_name)
rbdXML = RbdVolumeXMLBuilder()
device = rbdXML.construct(domain_name)
guest:Guest = create_domain(domain_name)
guest.devices.disk.append(device)
guest_manager.create_domain(conn, guest.get_xml_string())
domain_uuid = guest_manager.get_uuid_by_name(conn, guest.domain_name)
guest_manager.start_domain(conn, domain_uuid)

time2 = datetime.datetime.now()

print("台数："+ str(1) +"\n"+
      "开始时间："+ str(time1) +"\n"+
      "结束时间："+ str(time2)+"\n"+
      "开销时间："+ str(time2-time1))

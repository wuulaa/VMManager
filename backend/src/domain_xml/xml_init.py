import pdb
from src.domain_xml.domain.domainOs import DomainOs, BootDevice
from src.domain_xml.domain.features import DomainFeatures
from src.domain_xml.domain.cpu import DomainCpu
from src.domain_xml.device.controller import DeviceController
from src.domain_xml.device.char import DeviceSerial, DeviceConsole, CharSource, DeviceChannel
from src.domain_xml.device.graphics import create_local_auto_port_vnc_viewer, create_local_auto_port_spice_viewer
from src.domain_xml.device.input import DeviceInput
from src.domain_xml.domain.guest import Guest, DomainDevices

def create_initial_xml(domain_name: str, uuid: str, cpu: int, max_cpu: int, memory: int, max_memory: int, arch: str):
    guest = Guest()

    # set guest basic values
    guest.domain_name = domain_name
    guest.uuid = uuid
    guest.type = "kvm"
    guest.memoryUnit = "KiB"
    guest.memory = max_memory
    guest.currentMemory = memory
    guest.vcpus = max_cpu
    guest.vcpu_current = cpu
    guest.vcpu_placement = "static"

    # set os related values
    domainOS = DomainOs.create_default_os_builder(guest.domain_name, arch)

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
    if arch == 'arrch64':
        domainFeatures.gic = '3'
    else:
        domainFeatures.apic = ''
        domainFeatures.vmport = False
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
    # interface0, interface1 = create_interfaces("demoBridge", domain_name)
    # devices.interface.append(interface0)
    # devices.interface.append(interface1)
    guest.devices = devices

    # VNC
    vnc_viewer = create_local_auto_port_vnc_viewer()
    devices.graphics.append(vnc_viewer)
    
    # SPICE
    vnc_viewer = create_local_auto_port_spice_viewer()
    devices.graphics.append(vnc_viewer)

    # serial
    char_source = CharSource()
    char_source.path = '/dev/pts/2'

    serial = DeviceSerial()
    serial.type = 'pty'
    if arch == 'arrch64':
        serial.target_type = 'system-serial'
        serial.target_port = '0'
        serial.target_model_name = 'pl011'
        serial.source = char_source
    else:
        serial.target_type = 'isa-serial'
        serial.target_port = '0'
        serial.target_model_name = 'isa-serial'

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

    if arch == 'x86':
        guest.emulator = "/usr/bin/qemu-system-x86_64"
    else:
        guest.emulator = "/usr/bin/qemu-system-aarch64"
        domainFeatures.gic = '3'
    return guest

# print(create_initial_xml("test", "test", 2, 2, 20480, 20480, "x86").get_xml_string())
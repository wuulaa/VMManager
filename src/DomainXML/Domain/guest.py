from src.DomainXML.Device.input import DeviceInput
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
from src.DomainXML.Device.interface import *
from src.DomainXML.Device.char import DeviceSerial, DeviceConsole, CharSource, DeviceChannel
from src.DomainXML.Device.graphics import DeviceGraphics


class DomainDevices(XMLBuilder):
    XML_NAME = "devices"

    disk = XMLChildBuilder(DeviceDisk, is_single=False)
    controller = XMLChildBuilder(DeviceController, is_single=False)
    interface = XMLChildBuilder(DeviceInterface, is_single=False)
    serial = XMLChildBuilder(DeviceSerial, is_single=False)
    console = XMLChildBuilder(DeviceConsole, is_single=False)
    channel = XMLChildBuilder(DeviceChannel, is_single=False)
    graphics = XMLChildBuilder(DeviceGraphics, is_single=False)
    input = XMLChildBuilder(DeviceInput, is_single=False)
    # filesystem = XMLChildBuilder(DeviceFilesystem)
    # smartcard = XMLChildBuilder(DeviceSmartcard)
    # serial = XMLChildBuilder(DeviceSerial)
    # parallel = XMLChildBuilder(DeviceParallel)
    # console = XMLChildBuilder(DeviceConsole)
    # tpm = XMLChildBuilder(DeviceTpm)
    # sound = XMLChildBuilder(DeviceSound)
    # audio = XMLChildBuilder(DeviceAudio)
    # video = XMLChildBuilder(DeviceVideo)
    # hostdev = XMLChildBuilder(DeviceHostdev)
    # redirdev = XMLChildBuilder(DeviceRedirdev)
    # watchdog = XMLChildBuilder(DeviceWatchdog)
    # memballoon = XMLChildBuilder(DeviceMemballoon)
    # rng = XMLChildBuilder(DeviceRng)
    # panic = XMLChildBuilder(DevicePanic)
    # shmem = XMLChildBuilder(DeviceShMem)
    # memory = XMLChildBuilder(DeviceMemory)
    # vsock = XMLChildBuilder(DeviceVsock)
    # iommu = XMLChildBuilder(DeviceIommu)


class Guest(XMLBuilder):
    XML_NAME = "domain"

    domain_name = XMLProperty("./name")
    uuid = XMLProperty("./uuid")
    title = XMLProperty("./title")
    description = XMLProperty("./description")
    id = XMLProperty("./@id", is_int=True)
    type = XMLProperty("./@type")

    maxMemory = XMLProperty('./maxMemory', is_int=True)
    maxMemorySlots = XMLProperty("./maxMemory/@slots", is_int=True)
    maxMemoryUnit = XMLProperty("./maxMemory/@unit")

    memory = XMLProperty('./memory', is_int=True)
    memoryUnit = XMLProperty("./memory/@unit")

    currentMemory = XMLProperty('./currentMemory', is_int=True)
    currentMemoryUnit = XMLProperty("./currentMemory/@unit")

    vcpus = XMLProperty("./vcpu", is_int=True)
    vcpu_current = XMLProperty("./vcpu/@current", is_int=True)
    vcpu_placement = XMLProperty("./vcpu/@placement")
    vcpu_cpuset = XMLProperty("./vcpu/@cpuset")

    os = XMLChildBuilder(DomainOs, is_single=True)
    features = XMLChildBuilder(DomainFeatures, is_single=True)

    cpu = XMLChildBuilder(DomainCpu, is_single=True)
    clock = XMLChildBuilder(DomainClock, is_single=True)

    on_poweroff = XMLProperty("./on_poweroff")
    on_reboot = XMLProperty("./on_reboot")
    on_crash = XMLProperty("./on_crash")
    on_lockfailure = XMLProperty("./on_lockfailure")

    pm = XMLChildBuilder(DomainPm, is_single=True)

    emulator = XMLProperty("./devices/emulator")
    devices = XMLChildBuilder(DomainDevices, is_single=True)




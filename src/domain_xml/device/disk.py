"""
This file implements classes for managing libvirt disk xml
See https://libvirt.org/formatdomain.html#hard-drives-floppy-disks-cdroms
"""
from src.domain_xml.device.common import Auth, Host, Target
from src.utils.xml_builder.xml_builder import XMLBuilder, XMLProperty, XMLChildBuilder
from src.domain_xml.device.device import Device, DeviceSeclabel


# class DiskDriver(XMLBuilder):
#     """
#     example:
#     <driver name='qemu' type='raw'/>
#     <driver name='qemu' type='qcow2' queues='4' queue_size='256' />
#     """
#     XML_NAME = 'driver'
#     name = XMLProperty('./@name')
#     type = XMLProperty('./@type')
#
#     def set_defaults(self, cond=None):
#         self.name = 'qemu'
#
#
# class DiskSourceSnapshot(XMLBuilder):
#     """
#     example:
#     <snapshot name="snapname"/>
#     """
#     XML_NAME = 'snapshot'
#     name = './@name'
#
#
# class DiskSourceConfig(XMLBuilder):
#     """
#     example:
#     <config file="/path/to/file"/>
#     """
#     XML_NAME = 'config'
#     file = './@file'
#
#
# class DiskSource(XMLBuilder):
#     """
#     example:
#     <source protocol="rbd" name='libvirt-pool/new-libvirt-image'>
#       <host name="ceph1" port="6789"/>
#       <snapshot name="snapname"/>
#       <config file="/path/to/file"/>
#     </source>
#     """
#
#     XML_NAME = 'source'
#
#     protocol = XMLProperty('./@protocol')
#     name = XMLProperty('./@name')
#
#     host = XMLChildBuilder(Host)
#     # snapshot
#     snapshot_name = XMLProperty('./snapshot/@name')
#     # config
#     config_file = XMLProperty('./config/@file')
#
#
# class DeviceDisk(XMLBuilder):
#     XML_NAME = 'disk'
#
#     type = XMLProperty('./@type')
#     device = XMLProperty('./@device')
#
#     driver = XMLChildBuilder(DiskDriver)
#     source = XMLChildBuilder(DiskSource)
#     auth = XMLChildBuilder(Auth)
#     target = XMLChildBuilder(Target)
#
#     def set_defaults(self, cond=None):
#         self.device = 'disk'


class DiskSource(XMLBuilder):
    """
    Class representing disk <source> block, and various helpers
    that only operate on <source> contents
    """

    XML_NAME = "source"

    file = XMLProperty("./@file")
    dev = XMLProperty("./@dev")
    dir = XMLProperty("./@dir")

    pool = XMLProperty("./@pool")
    volume = XMLProperty("./@volume")
    mode = XMLProperty("./@mode")

    host = XMLChildBuilder(Host)

    name = XMLProperty("./@name")
    protocol = XMLProperty("./@protocol")
    query = XMLProperty("./@query")

    type = XMLProperty("./@type")
    managed = XMLProperty("./@managed", is_yesno=True)
    namespace = XMLProperty("./@namespace", is_int=True)


class DeviceDisk(XMLBuilder):
    XML_NAME = "disk"

    DEVICE_DISK = "disk"
    DEVICE_LUN = "lun"
    DEVICE_CDROM = "cdrom"
    DEVICE_FLOPPY = "floppy"

    TYPE_FILE = "file"
    TYPE_BLOCK = "block"
    TYPE_DIR = "dir"
    TYPE_VOLUME = "volume"
    TYPE_NETWORK = "network"

    type = XMLProperty("./@type")
    device = XMLProperty("./@device")

    driver_name = XMLProperty("./driver/@name")
    driver_type = XMLProperty("./driver/@type")

    source = XMLChildBuilder(DiskSource)

    auth = XMLChildBuilder(Auth)

    # snapshot_policy = XMLProperty("./@snapshot")

    target_bus = XMLProperty("./target/@bus")
    target_dev = XMLProperty("./target/@dev")
    target_tray = XMLProperty('./target/@tray', is_openclose=True)
    removable = XMLProperty("./target/@removable", is_onoff=True)
    rotation_rate = XMLProperty("./target/@rotation_rate", is_int=True)

    read_only = XMLProperty("./readonly", is_bool=True)
    shareable = XMLProperty("./shareable", is_bool=True)
    transient = XMLProperty("./transient", is_bool=True)
    transient_shareBacking = XMLProperty(
        "./transient/@shareBacking", is_yesno=True)

    driver_copy_on_read = XMLProperty("./driver/@copy_on_read", is_onoff=True)
    driver_cache = XMLProperty("./driver/@cache")
    driver_discard = XMLProperty("./driver/@discard")
    driver_detect_zeroes = XMLProperty("./driver/@detect_zeroes")
    driver_io = XMLProperty("./driver/@io")
    driver_iothread = XMLProperty("./driver/@iothread", is_int=True)
    driver_queues = XMLProperty("./driver/@queues", is_int=True)

    def set_defaults(self, cond=None, **kwargs):
        self.driver_name = 'qemu'
        self.driver_type = 'raw'
        if ('disk_device' not in kwargs):
            self.device = 'disk'
        else:
            self.device = kwargs.get('disk_device')

    #############################
    # Internal defaults helpers #
    #############################

    def _get_default_type(self):
        if self.source.pool or self.source.volume:
            return DeviceDisk.TYPE_VOLUME
        if self.source.protocol:
            return DeviceDisk.TYPE_NETWORK
        return self.TYPE_FILE

    def _get_default_driver_name(self):
        if self.is_empty():
            return None

        # Recommended xen defaults from here:
        # https://bugzilla.redhat.com/show_bug.cgi?id=1171550#c9
        # If type block, use name=phy. Otherwise do the same as qemu
        if self.conn.is_xen() and self.type == self.TYPE_BLOCK:
            return self.DRIVER_NAME_PHY
        if self.conn.support.conn_disk_driver_name_qemu():
            return self.DRIVER_NAME_QEMU
        return None

    ###########################
    # Misc functional helpers #
    ###########################

    def get_target_prefix(self):
        """
        Returns the suggested disk target prefix (hd, xvd, sd ...) for the
        disk.
        :returns: str prefix, or None if no reasonable guess can be made
        """
        # The upper limits here aren't necessarily 1024, but let the HV
        # error as appropriate.
        def _return(prefix):
            nummap = {
                "vd": 1024,
                "xvd": 1024,
                "fd": 2,
                "hd": 4,
                "sd": 1024,
            }
            return prefix, nummap[prefix]

        if self.target_bus == "virtio":
            return _return("vd")
        elif self.target_bus == "xen":
            return _return("xvd")
        elif self.target_bus == "fdc" or self.is_floppy():
            return _return("fd")
        elif self.target_bus == "ide":
            return _return("hd")
        # sata, scsi, usb, sd
        return _return("sd")

    def generate_target(self, skip_targets):
        """
        Generate target device ('hda', 'sdb', etc..) for disk, excluding
        any targets in 'skip_targets'.
        Sets self.target, and returns the generated value.

        :param skip_targets: list of targets to exclude
        :returns: generated target
        """
        prefix, maxnode = self.get_target_prefix()
        skip_targets = [t for t in skip_targets if t and t.startswith(prefix)]
        skip_targets.sort()

        def get_target():
            first_found = None

            for i in range(maxnode):
                gen_t = prefix + self.num_to_target(i + 1)
                if gen_t in skip_targets:
                    skip_targets.remove(gen_t)
                    continue
                if not skip_targets:
                    return gen_t
                elif not first_found:
                    first_found = gen_t
            if first_found:
                return first_found

        ret = get_target()
        if ret:
            self.target = ret
            return ret

        raise ValueError(
            ("Only %(number)s disk for bus '%(bus)s' are supported",
             "Only %(number)s disks for bus '%(bus)s' are supported",
             maxnode) %
            {"number": maxnode, "bus": self.bus})


####################
# Helper Functions #
####################
def create_disk_builder(source_path: str = None,
                        target_dev: str = None):
    '''
    <disk type='file' device='disk'>
        <driver name='qemu' type='qcow2'/>
        <source file='/home/kvm/images/xavier1.img'/>
        <target dev='vda' bus='virtio'/>
        <alias name='virtio-disk0'/>
        <address type='pci' domain='0x0000' bus='0x04' slot='0x00' function='0x0'/>
    </disk>
    '''
    disk = DeviceDisk()
    disk.type = 'file'
    disk.device = 'disk'
    disk.driver_type = 'qcow2'

    source = DiskSource()
    source.file = source_path
    disk.source = source

    # target
    disk.target_dev = target_dev
    disk.target_bus = 'virtio'

    return disk


def create_cdrom_builder(source_path: str = None,
                         target_dev: str = None):
    '''
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <source file='/home/kvm/images/CentOS-7-aarch64-Everything-2009.iso'/>
      <backingStore/>
      <target dev='sda' bus='scsi'/>
      <readonly/>
      <alias name='scsi0-0-0-0'/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
    '''
    disk = DeviceDisk()
    disk.type = 'file'
    disk.device = 'cdrom'

    source = DiskSource()
    source.file = source_path
    disk.source = source

    disk.target_dev = target_dev
    disk.target_bus = 'scsi'
    disk.read_only = True

    return disk


# common_disk = create_disk_builder(source_path='/home/kvm/images/xavier1.img',
#                                   target_dev='vdb')
# print(common_disk.get_xml_string())
#
# print('----------------------------------------')
#
# cdrom = create_cdrom_builder(
#     source_path='/home/kvm/images/CentOS-7-aarch64-Everything-2009.iso',
#     target_dev='sda')
# print(cdrom.get_xml_string())

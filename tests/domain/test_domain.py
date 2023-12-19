import sys
import os
sys.path.append(os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')))
from src.manage.domain_manage import *
from src.utils.connect import *

conn = get_connected(User="root@172.16.2.83")

testXML = '''
<domain type='kvm'>
  <name>''' + "zyq_test" + '''</name> 
  <memory unit='KiB'>8388608</memory>
  <currentMemory unit='KiB'>8388608</currentMemory>
  <vcpu placement='static'>4</vcpu>
  <os>
    <type arch='aarch64' machine='virt-rhel7.6.0'>hvm</type>
    <loader readonly='yes' type='pflash'>/usr/share/AAVMF/AAVMF_CODE.fd</loader>
    <nvram>/var/lib/libvirt/qemu/nvram/zyq_test_VARS.fd</nvram>
    <boot dev='hd'/>
  </os>
  <features>
    <acpi/>
    <gic version='3'/>
  </features>
 <clock offset='utc'/>
 <on_poweroff>destroy</on_poweroff> 
 <on_reboot>restart</on_reboot>
 <on_crash>restart</on_crash>  
 <devices>
   <emulator>/usr/libexec/qemu-kvm</emulator>
  <disk type='file' device='disk'>
      <driver name='qemu' type='qcow2'/>
      <source file='/home/kvm/images/zyq_test.img'/>
      <target dev='vda' bus='virtio'/>
      <address type='pci' domain='0x0000' bus='0x04' slot='0x00' function='0x0'/>
    </disk>
    <disk type='file' device='cdrom'>
      <driver name='qemu' type='raw'/>
      <target dev='sda' bus='scsi'/>
      <readonly/>
      <address type='drive' controller='0' bus='0' target='0' unit='0'/>
    </disk>
   <interface type='network'>
     <source network='default'/>
   </interface>  
   <graphics type='vnc' port='-1' autoport='yes' listen='0.0.0.0'>
     <listen type='address' address='0.0.0.0'/>
   </graphics>
 </devices>
</domain>
'''


def test_creat_domain(conn, testXML):
    result = create_domain(conn, testXML)
    assert result["is_success"] == True


def test_delete_domain(conn: libvirt.virConnect, domain_flag):
    result = delete_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_destroy_domain(conn: libvirt.virConnect, domain_flag):
    result = destroy_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_suspend_domain(conn: libvirt.virConnect, domain_flag):
    result = suspend_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_reboot_domain(conn: libvirt.virConnect, domain_flag):
    result = reboot_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_resume_domain(conn: libvirt.virConnect, domain_flag):
    result = resume_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_set_auto_start(conn: libvirt.virConnect, domain_flag):
    result = set_auto_start(conn, domain_flag)
    assert result["is_success"] == True


def test_shutdown_domain(conn: libvirt.virConnect, domain_flag):
    result = shutdown_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_start_domain(conn: libvirt.virConnect, domain_flag):
    result = start_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_status_domains(conn: libvirt.virConnect, domain_flag):
    result = status_domain(conn, domain_flag)
    assert result["is_success"] == True


def test_batch_start_domains(conn: libvirt.virConnect, domain_flag):
    result = batch_start_domains(conn, domain_flag)


def test_batch_suspend_domains(conn: libvirt.virConnect, domain_flag):
    result = batch_suspend_domains(conn, domain_flag)


def test_batch_del_domains(conn: libvirt.virConnect, domain_flag):
    result = batch_del_domains(conn, domain_flag)


def test_batch_restart_domains(conn: libvirt.virConnect, domain_flag):
    result = batch_restart_domains(conn, domain_flag)

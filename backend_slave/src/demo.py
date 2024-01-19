from src.domain_manager.guest import *

conn = libvirt.open("qemu:///system")
if not conn:
    raise SystemExit("Failed to open connection to qemu:///system")

xml = '''<domain type="kvm">
  <name>template1</name>
  <memory unit="KiB">1048576</memory>
  <currentMemory>1048576</currentMemory>
  <vcpu placement="static">2</vcpu>
  <os>
    <type arch="aarch64" machine="virt-6.2">hvm</type>
    <loader readonly="no" type="pflash">/usr/share/AAVMF/AAVMF_CODE.ms.fd</loader>
    <nvram template="/usr/share/AAVMF/AAVMF_CODE.ms.fd">/var/lib/libvirt/qemu/nvram/template1_VARS.fd</nvram>
    <boot dev="cdrom"/>
    <boot dev="hd"/>
  </os>
  <features>
    <acpi></acpi>
    <gic version="3"/>
  </features>
  <cpu mode="host-passthrough" check="none"/>
  <on_poweroff>destroy</on_poweroff>
  <on_reboot>restart</on_reboot>
  <on_crash>destroy</on_crash>
  <devices>
    <controller type="scsi" index="0" model="virtio-scsi"/>
    <controller type="usb" index="0" model="qemu-xhci" ports="15"/>
    <input type="mouse" bus="usb"/>
    <input type="keyboard" bus="usb"/>
    <serial type="pty">
      <target type="system-serial" port="0">
        <model name="pl011"/>
      </target>
      <source path="/dev/pts/2"/>
    </serial>
    <console type="pty" tty="/dev/pts/2">
      <target type="serial" port="0"/>
      <source path="/dev/pts/2"/>
    </console>
    <channel type="unix">
      <target type="virtio" name="org.qemu.guest_agent.0"/>
    </channel>
    <emulator>/usr/bin/qemu-system-aarch64</emulator>
    <disk device="disk" type="network">
      <driver name="qemu" type="raw"/>
      <target dev="vda" bus="virtio"/>
      <auth username="volume">
        <secret type="ceph" uuid="55dc5fc7-6948-4fc9-8dc3-d563c2dee7b4"/>
      </auth>
      <source protocol="rbd" name="volume-pool/template1">
        <host name="kunpeng" port="6789"/>
      </source>
    </disk>
    <disk device="cdrom" type="file">
      <driver name="qemu" type="raw"/>
      <source file="/home/kvm/images/ubuntu-22.04.3-live-server-arm64.iso"/>
      <target dev="sda" bus="scsi"/>
      <readonly>True</readonly>
    </disk>
  </devices>
</domain>'''

create_persistent_domain(conn, xml)
domain_uuid = get_uuid_by_name(conn, "template1")
start_domain(conn, domain_uuid)
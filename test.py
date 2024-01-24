import libvirt
conn = libvirt.open("qemu:///system")

domain = conn.lookupByName("york3")
# print(domain.vcpusFlags(libvirt.VIR_DOMAIN_VCPU_MAXIMUM))
flags =  libvirt.VIR_DOMAIN_VCPU_MAXIMUM | libvirt.VIR_DOMAIN_AFFECT_CONFIG
domain.setVcpusFlags(10, flags)
print(domain.vcpusFlags(libvirt.VIR_DOMAIN_VCPU_MAXIMUM))
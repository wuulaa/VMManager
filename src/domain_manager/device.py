import libvirt
import src.domain_manager.conf.conf as device_constrains


def set_domain_name(domain: libvirt.virDomain, name: str) -> dict:
    length_constrain = device_constrains.MAX_DOMAIN_NAME_LENGTH
    if len(name) > length_constrain:
        description = "The length of domain name cannot exceed {length}".format(
            length=length_constrain)
        return {
            "is_success": False,
            "description": description
        }
    try:
        domain.rename(name)
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


def set_domain_description(domain: libvirt.virDomain, description: str) -> dict:
    domain.setMetadata(
        libvirt.VIR_DOMAIN_METADATA_DESCRIPTION,
        description,
        None,
        None)
    return {
        "is_success": True
    }


def set_domain_title(domain: libvirt.virDomain, title: str) -> dict:
    domain.setMetadata(libvirt.VIR_DOMAIN_METADATA_TITLE, title, None, None)
    return {
        "is_success": True
    }


def set_domain_vcpu(
        domain: libvirt.virDomain,
        vcpu: int,
        flags: int = libvirt.VIR_DOMAIN_VCPU_CURRENT
) -> dict:
    max_cpu = domain.vcpusFlags(libvirt.VIR_DOMAIN_VCPU_MAXIMUM)
    try:
        if flags == (libvirt.VIR_DOMAIN_VCPU_MAXIMUM | libvirt.VIR_DOMAIN_VCPU_LIVE):
            domain.setVcpusFlags(vcpu, flags)
        elif vcpu > max_cpu:
            return {
                "is_success": False,
                "description": "The vcpu number exceeds the max limit of {max_num}".format(max_num=max_cpu)
            }
        else:
            domain.setVcpusFlags(vcpu, flags)
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


def set_domain_memory(domain: libvirt.virDomain, memory: int, flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT) -> dict:
    max_memory = domain.maxMemory()
    try:
        if flags == libvirt.VIR_DOMAIN_MEM_MAXIMUM:
            domain.setMemoryFlags(memory, flags)
        elif memory > max_memory:
            return {
                "is_success": False,
                "description": "The memory size exceeds the max limit of {max_num}".format(max_num=max_memory)
            }
        else:
            domain.setMemoryFlags(memory, flags)
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


def attach_device_to_domain(domain: libvirt.virDomain, xml: str, flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT) -> dict:
    try:
        domain.attachDeviceFlags(xml, flags)
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


def detach_device_from_domain(domain: libvirt.virDomain, xml: str, flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT) -> dict:
    try:
        domain.detachDeviceFlags(xml, flags)
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


def update_domain_device(domain: libvirt.virDomain, xml: str, flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT) -> dict:
    try:
        domain.updateDeviceFlags(xml, flags)
        return {
            "is_success": True
        }
    except libvirt.libvirtError as e:
        return {
            "is_success": False,
            "description": str(e)
        }


####################
# Helper Functions #
####################

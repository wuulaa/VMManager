import libvirt
import src.domain_manager.conf.conf as device_constrains
from src.utils.response import APIResponse

error_info = {
    400:"Unkown exception.",
    401:"Count Exceeds limit",
    404:"VM not found."
    
}

def set_domain_name(conn: libvirt.virConnect, domain_uuid: str, name: str):
    '''set domain name'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        
        length_constrain = device_constrains.MAX_DOMAIN_NAME_LENGTH
        if len(name) > length_constrain:
            description = "The length of domain name cannot exceed {length}".format(
                length=length_constrain)
            return APIResponse.error(code=401, msg=description)
        
        domain.rename(name)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


def set_domain_vcpu(
        conn: libvirt.virConnect, 
        domain_uuid: str,
        vcpu: int,
        flags: int = libvirt.VIR_DOMAIN_VCPU_CURRENT):
    '''set domain vcpu'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        
        max_cpu = domain.vcpusFlags(libvirt.VIR_DOMAIN_VCPU_MAXIMUM)
        if flags == (libvirt.VIR_DOMAIN_VCPU_MAXIMUM | libvirt.VIR_DOMAIN_VCPU_LIVE):
            domain.setVcpusFlags(vcpu, flags)
        elif vcpu > max_cpu:
            return APIResponse.error(code=401, msg=error_info.get(401))
        else:
            domain.setVcpusFlags(vcpu, flags)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


def set_domain_memory(conn: libvirt.virConnect, 
                      domain_uuid: str, 
                      memory: int, 
                      flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT):
    '''set domain memory'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        max_memory = domain.maxMemory()
        
        if flags == libvirt.VIR_DOMAIN_MEM_MAXIMUM:
            domain.setMemoryFlags(memory, flags)
        elif memory > max_memory:
            description = "The memory size exceeds the max limit of {max_num}".format(max_num=max_memory)
            return APIResponse.error(code=401, msg=description)
        else:
            domain.setMemoryFlags(memory, flags)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


def attach_device_to_domain(conn: libvirt.virConnect, 
                            domain_uuid: str, 
                            xml: str, 
                            flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT):
    '''attach device to domain'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        domain.attachDeviceFlags(xml, flags)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


def detach_device_from_domain(conn: libvirt.virConnect, 
                              domain_uuid: str,
                              xml: str,
                              flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT):
    '''detach device from domain'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        domain.detachDeviceFlags(xml, flags)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


def update_domain_device(conn: libvirt.virConnect, 
                         domain_uuid: str,
                         xml: str,
                         flags: int = libvirt.VIR_DOMAIN_AFFECT_CURRENT):
    '''update domain device'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        domain.updateDeviceFlags(xml, flags)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


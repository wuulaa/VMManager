import libvirt
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
        
        length_constrain = 64
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
        # flags = 4 | 2, change the maxium
        if flags == (libvirt.VIR_DOMAIN_VCPU_MAXIMUM | libvirt.VIR_DOMAIN_AFFECT_CONFIG):
            domain.setVcpusFlags(vcpu, flags)
        # else change with given flags, can not exceed maxium
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
    

def get_domain_interface_addresses(conn: libvirt.virConnect, domain_uuid: str):
    '''
    get domain interface addressees using qga, returned as dict.
    domain should be running
    '''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        res = domain.interfaceAddresses(libvirt.VIR_DOMAIN_INTERFACE_ADDRESSES_SRC_AGENT)
        return APIResponse.success(res)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


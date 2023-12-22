import libvirt
from utils.response import APIResponse

states = {
    0:"nostate",
    1:"running",
    2:"blocked",
    3:"paused",
    4:"shutdown",
    5:"shutoff",
    6:"crashed",
    7:"pmsuspended"
}

error_info = {
    400:"Unkown exception.",
    1:"VM state is error."
}

def create_persistent_domain(conn: libvirt.virConnect, confingXML):
    '''create a persistent domain '''

    try:
        domain = conn.defineXML(confingXML)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))
    else:
        return APIResponse.success(data={"domain_name":domain.name})
    

def create_unpersistent_domain(conn: libvirt.virConnect, confingXML):
    '''create a unpersistent domain '''

    try:
        domain = conn.createXML(confingXML)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, mag=str(err))
    else:
        return APIResponse.success(data={"domain_name":domain.name})


def delete_domain(conn: libvirt.virConnect, domain_uuid, flags=4):
    '''
        undefine domain
        flags:1 Also remove any managed save
        flags:2 If last use of domain, then also remove any snapshot metadata
        flags:4 Also remove any nvram file
        flags:8 Keep nvram file
        flags:16 If last use of domain, then also remove any checkpoint metadata
        flags:32 Also remove any TPM state
        flags:64 Keep TPM state Future undefine control flags should come here.
    '''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400,msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        elif domain.state()[0] is libvirt.VIR_DOMAIN_SHUTOFF:
            domain.undefineFlags(flags)
            return APIResponse.success()
        else:
            return APIResponse.error(code=1,mas="error: Failed to undefine domain. Domain"
                    + domain_uuid+"isn't shutoff.")
        


def destroy_domain(conn: libvirt.virConnect, domain_uuid):
    '''destroy domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400,msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        elif (domain.state()[0] is libvirt.VIR_DOMAIN_RUNNING
              or domain.state()[0]  is libvirt.VIR_DOMAIN_CRASHED):
            domain.destroy()
            return APIResponse.success()
        else:
            return APIResponse.error(code=1, msg="error: Failed to destroy domain. Domain" +
                    domain_uuid+"state is error. ")


def pause_domain(conn: libvirt.virConnect, domain_uuid):
    '''suspend domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400, msg="error: Domain is none.")
        elif domain.state()[0] is libvirt.VIR_DOMAIN_RUNNING:
            domain.suspend()
            return APIResponse.success()
        else:
            return APIResponse.error(code=1, msg=error_info[1] + " Failed to suspend domain. Domain" +
                    domain_uuid+"isn't running. ")


def reboot_domain(conn: libvirt.virConnect, domain_uuid):
    '''reboot domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        elif domain.state()[0] is libvirt.VIR_DOMAIN_RUNNING:
            domain.reboot()
            return APIResponse.success()
        else:
            return APIResponse.error(code=1, msg="error: Failed to reboot domain. Domain"
                    + domain_uuid+"isn't running. ")


def resume_domain(conn: libvirt.virConnect, domain_uuid):
    '''resume domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        elif domain.state()[0] is libvirt.VIR_DOMAIN_PAUSED:
            domain.resume()
            return {"is_success": True}
        else:
            return APIResponse.error(code=1, msg="error: Failed to resume domain. Domain"
                    + domain_uuid+"state is error. ")


def set_auto_start(conn: libvirt.virConnect, domain_uuid):
    '''set_auto_start'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        else:
            domain.setAutostart(1)
            return APIResponse.success()


def shutdown_domain(conn: libvirt.virConnect, domain_uuid):
    '''shutdown domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        elif domain.state()[0] is libvirt.VIR_DOMAIN_RUNNING:
            domain.shutdown()
            return APIResponse.success()
        else:
            return APIResponse.error(code=1, msg="error: Failed to shutdown domain.  Domain"
                    + domain_uuid+"state is error. ")


def start_domain(conn: libvirt.virConnect, domain_uuid):
    '''start domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        elif domain.state()[0] is libvirt.VIR_DOMAIN_SHUTOFF:
            domain.create()
            return APIResponse.success()
        else:
            return APIResponse.error(code=1, msg="error: Failed to shutdown domain. Domain"
                    + domain_uuid+"state is error. ")
        
def rename_domain(conn: libvirt.virConnect, domain_uuid: str, domain_new_name: str):
    '''rename a domain'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    else:
        if domain is None:
            return APIResponse.error(code=400,msg="domain is none.")
        else:
            try:
                domain.rename(domain_new_name)
                return APIResponse.success()
            except libvirt.libvirtError as err:
                return APIResponse.error(code=400, msg=str(err))


def get_domains_list(conn: libvirt.virConnect):
    '''
        get domains state info
        return:{domain_name,domain_state}
    '''
    result = dict()
    domains = conn.listAllDomains()
    for domain in domains:
        result[domain.name()] = states[domain.state()[0]]
    return result


def get_domain_detail_info(conn: libvirt.virConnect, domain_uuid):
    domain: libvirt.virDomain = conn.lookupByUUIDString(domain_uuid)
    return domain.info()


def get_uuid_by_name(conn: libvirt.virConnect, name: str):
    return conn.lookupByName(name).UUIDString()


def batch_start_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch start domains'''
    failed_list =[]
    success_list=[]
    for uuid in domain_uuid_list:
        if(start_domain(conn, uuid).code != 0):
            failed_list.append(uuid)
        else:
            success_list.append(uuid)
    if(failed_list.__len__==0):
        return APIResponse.success(success_list)
    else:
        return APIResponse.error(msg=failed_list)


def batch_suspend_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch suspend domains'''
    for uuid in domain_uuid_list:
        pause_domain(conn, uuid)


def batch_shutdown(conn: libvirt.virConnect, domain_uuid_list):
    '''batch shutdown domains'''
    for uuid in domain_uuid_list:
        shutdown_domain(conn, uuid)


def batch_del_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch delete domains'''
    for uuid in domain_uuid_list:
        delete_domain(conn, uuid)


def batch_restart_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch reboot domains'''
    for uuid in domain_uuid_list:
        reboot_domain(conn, uuid)

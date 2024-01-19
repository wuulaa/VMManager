import libvirt
from xml.etree import ElementTree
from src.utils.response import APIResponse

status = {
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
        return APIResponse.error(code=400, msg=str(err))
    else:
        return APIResponse.success(data={"domain_name":domain.name})
    

def create_unpersistent_domain(conn: libvirt.virConnect, confingXML):
    '''create a unpersistent domain '''

    try:
        domain = conn.createXML(confingXML)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
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


def restart_domain(conn: libvirt.virConnect, domain_uuid):
    '''restart domain'''

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
            return APIResponse.error(code=1, msg="error: Failed to restart domain. Domain"
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
        result[domain.name()] = status[domain.state()[0]]
    return result


def set_domain_description(conn: libvirt.virConnect, domain_uuid: str, description: str):
    '''set domain description'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        domain.setMetadata(
        libvirt.VIR_DOMAIN_METADATA_DESCRIPTION, description, None, None)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    

def set_domain_title(conn: libvirt.virConnect, domain_uuid: str, title: str):
    '''set domain title'''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        domain.setMetadata(libvirt.VIR_DOMAIN_METADATA_TITLE, title, None, None)
        return APIResponse.success()
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))


def get_domain_detail_info(conn: libvirt.virConnect, domain_uuid):
    domain: libvirt.virDomain = conn.lookupByUUIDString(domain_uuid)
    return domain.info()


def get_uuid_by_name(conn: libvirt.virConnect, name: str):
    return conn.lookupByName(name).UUIDString()


def get_domain_monitor_status(conn: libvirt.virConnect, domain_uuid: str):
    '''
    get domain monitor status, including cpu, memory, interfaces and disks
    '''
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        if domain is None:
            return APIResponse.error(code=404, msg=error_info.get(404))
        # memory
        memory_status = domain.memoryStats()
        
        # cpu
        cpu_status = domain.getCPUStats(True)
        
        # iface
        iface_stats = []
        tree = ElementTree.fromstring(domain.XMLDesc())
        ifaces = tree.findall('devices/interface/target')
        for i in ifaces:
            iface = i.get('dev')
            ifaceinfo = domain.interfaceStats(iface)
            iface_stat = {
                "name": iface,
                "info": ifaceinfo
            }
            iface_stats.append(iface_stat)
        
        # disk
        disk_stats = []
        disks = tree.findall('devices/disk/target')
        for d in disks:
            disk = d.get('dev')
            disk_info = domain.blockInfo(disk)
            disk_stat = {
                "name": disk,
                "info": disk_info
            }
            disk_stats.append(disk_stat)
        
        res = {
            "name": domain.name(),
            "memory": memory_status,
            "cpu": cpu_status,
            "interface": iface_stats,
            "disk": disk_stats
        }
        return APIResponse.success(res)
    except libvirt.libvirtError as err:
        return APIResponse.error(code=400, msg=str(err))
    

def set_user_passwd(conn: libvirt.virConnect, domain_uuid: str, user_name: str, passwd: str):
    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        domain.setUserPassword(user_name, passwd)
        return APIResponse.success()
    except libvirt.libvirtError as e:
        return APIResponse.error(code=400, msg=str(e))


def batch_start_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch start domains'''
    failed_list =[]
    success_list=[]
    for i in  range(0, len(domain_uuid_list)):
        result = start_domain(conn, domain_uuid_list[i])
        if(result.code != 0):
            failed_list += domain_uuid_list[i:]
            break
        else:
            success_list.append(domain_uuid_list[i])
    if(len(failed_list)==0):
        return APIResponse.success(success_list)
    else:
        response = APIResponse()
        response.set_data(dict = {
            "success:":success_list[0:],
            "error":failed_list[0]
        })
        response.set_code(400)
        response.set_msg("failed to batch operate. "+ failed_list[0] + result.msg)
        return response


def batch_pause_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch pause domains'''
    failed_list =[]
    success_list=[]
    for i in  range(0, len(domain_uuid_list)):
        result = pause_domain(conn, domain_uuid_list[i])
        if(result.code != 0):
            failed_list += domain_uuid_list[i:]
            break
        else:
            success_list.append(domain_uuid_list[i])
    if(len(failed_list)==0):
        return APIResponse.success(success_list)
    else:
        response = APIResponse()
        response.set_data(dict = {
            "success:":success_list[0:],
            "error":failed_list[0]
        })
        response.set_code(400)
        response.set_msg("failed to batch operate. "+ failed_list[0] + result.msg)
        return response


def batch_shutdown_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch shutdown domains'''
    failed_list =[]
    success_list=[]
    for i in  range(0, len(domain_uuid_list)):
        result = shutdown_domain(conn, domain_uuid_list[i])
        if(result.code != 0):
            failed_list += domain_uuid_list[i:]
            break
        else:
            success_list.append(domain_uuid_list[i])
    if(len(failed_list)==0):
        return APIResponse.success(success_list)
    else:
        response = APIResponse()
        response.set_data(dict = {
            "success:":success_list[0:],
            "error":failed_list[0]
        })
        response.set_code(400)
        response.set_msg("failed to batch operate. "+ failed_list[0] + result.msg)
        return response


def batch_delete_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch delete domains'''
    failed_list =[]
    success_list=[]
    for i in  range(0, len(domain_uuid_list)):
        result = delete_domain(conn, domain_uuid_list[i])
        if(result.code != 0):
            failed_list += domain_uuid_list[i:]
            break
        else:
            success_list.append(domain_uuid_list[i])
    if(len(failed_list)==0):
        return APIResponse.success(success_list)
    else:
        response = APIResponse()
        response.set_data(dict = {
            "success:":success_list[0:],
            "error":failed_list[0]
        })
        response.set_code(400)
        response.set_msg("failed to batch operate. "+ failed_list[0] + result.msg)
        return response


def batch_restart_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch restart domains'''
    failed_list =[]
    success_list=[]
    for i in  range(0, len(domain_uuid_list)):
        result = restart_domain(conn, domain_uuid_list[i])
        if(result.code != 0):
            failed_list += domain_uuid_list[i:]
            break
        else:
            success_list.append(domain_uuid_list[i])
    if(len(failed_list)==0):
        return APIResponse.success(success_list)
    else:
        response = APIResponse()
        response.set_data(dict = {
            "success:":success_list[0:],
            "error":failed_list[0]
        })
        response.set_code(400)
        response.set_msg("failed to batch operate. "+ failed_list[0] + result.msg)
        return response

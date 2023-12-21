import libvirt

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

def create_persistent_domain(conn: libvirt.virConnect, confingXML):
    '''create a persistent domain '''

    try:
        domain = conn.defineXML(confingXML)
    except libvirt.libvirtError as err:
        return {
            "is_success": False,
            "description": "error: Failed to creat domain."
            + str(err), "domain": None
        }
    else:
        return {
            "is_success": True,
            "domain_name": domain.name, "domain_ID": domain.ID
        }

def create_unpersistent_domain(conn: libvirt.virConnect, confingXML):
    '''create a unpersistent domain '''

    try:
        domain = conn.createXML(confingXML)
    except libvirt.libvirtError as err:
        return {
            "is_success": False,
            "description": "error: Failed to creat domain."
            + str(err), "domain": None
        }
    else:
        return {
            "is_success": True,
            "domain_name": domain.name, "domain_ID": domain.ID
        }


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
        return {"is_success": False,
                "description": "error: Failed to undefine domain."
                + str(err)}
    else:
        if domain is None:
            return {"is_success": False,
                    "description": "error: Domain is none."}
        elif domain.state()[0] is libvirt.VIR_DOMAIN_SHUTOFF:
            domain.undefineFlags(flags)
            return {"is_success": True}
        else:
            return {"is_success": False,
                    "description":  "error: Failed to undefine domain. Domain"
                    + domain_uuid+"isn't shutoff."}


def destroy_domain(conn: libvirt.virConnect, domain_uuid):
    '''destroy domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
        state = domain.state()[0]
    except libvirt.libvirtError as err:
        return {"is_success": False,
                "description": "error: Failed to destroy domain. "
                + str(err)}
    else:
        if domain is None:
            return {"is_success": False,
                    "description": "error: Domain is none."}
        elif (state is libvirt.VIR_DOMAIN_RUNNING
              or state is libvirt.VIR_DOMAIN_CRASHED):
            domain.destroy()
            return {"is_success": True}
        else:
            return {"is_success": False,
                    "description": "error: Failed to destroy domain. Domain" +
                    domain_uuid+"state is error. "}


def suspend_domain(conn: libvirt.virConnect, domain_uuid):
    '''suspend domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return {"is_success": False,
                "description": "error: Failed to suspend domain. "
                + str(err)}
    else:
        if domain is None:
            return {"is_success": False,
                    "description": "error: Domain is none. "}
        elif domain.state()[0] is libvirt.VIR_DOMAIN_RUNNING:
            domain.suspend()
            return {"is_success": True}
        else:
            return {"is_success": False,
                    "description": "error: Failed to suspend domain. Domain" +
                    domain_uuid+"isn't running. "}


def reboot_domain(conn: libvirt.virConnect, domain_uuid):
    '''reboot domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return {"is_success": False,
                "description": "error: Failed to reboot domain. "+str(err)}
    else:
        if domain is None:
            return {"is_success": False,
                    "description": "error: Domain is none. "}
        elif domain.state()[0] is libvirt.VIR_DOMAIN_RUNNING:
            domain.reboot()
            return {"is_success": True, "description": "Reboot successfully. "}
        else:
            return {"is_success": False,
                    "description": "error: Failed to reboot domain. Domain"
                    + domain_uuid+"isn't running. "}


def resume_domain(conn: libvirt.virConnect, domain_uuid):
    '''resume domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return {"is_success": False,
                "description": "error: Failed to resume domain. "+str(err)}
    else:
        if domain is None:
            return {"is_success": False,
                    "description": "error: Domain is none. "}
        elif domain.state()[0] is libvirt.VIR_DOMAIN_PAUSED:
            domain.resume()
            return {"is_success": True}
        else:
            return {"is_success": False,
                    "description": "error: Failed to resume domain. Domain"
                    + domain_uuid+"state is error. "}


def set_auto_start(conn: libvirt.virConnect, domain_uuid):
    '''set_auto_start'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return {"is_success": False,
                "description": "Failed to set_auto_start domain. "
                + str(err)}
    else:
        if domain is None:
            return {"is_success": False, "description": "Domain is none. "}
        else:
            domain.setAutostart(1)
            return {"is_success": True}


def shutdown_domain(conn: libvirt.virConnect, domain_uuid):
    '''shutdown domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return {"is_success": False,
                "description": "error: Failed to shutdown domain. "+str(err)}
    else:
        if domain is None:
            return {"is_success": False,
                    "description": "error: Domain is none. "}
        elif domain.state()[0] is libvirt.VIR_DOMAIN_RUNNING:
            domain.shutdown()
            return {"is_success": True}
        else:
            return {"is_success": False,
                    "description": "error: Failed to shutdown domain.  Domain"
                    + domain_uuid+"state is error. "}


def start_domain(conn: libvirt.virConnect, domain_uuid):
    '''start domain'''

    try:
        domain = conn.lookupByUUIDString(domain_uuid)
    except libvirt.libvirtError as err:
        return {"is_success": False,
                "description": "error: Failed to start domain. "+str(err)}
    else:
        if domain is None:
            return {"is_success": False,
                    "description": "error: Domain is none. "}
        elif domain.state()[0] is libvirt.VIR_DOMAIN_SHUTOFF:
            domain.create()
            return {"is_success": True}
        else:
            return {"is_success": False,
                    "description": "error: Failed to shutdown domain. Domain"
                    + domain_uuid+"state is error. "}


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
    for uuid in domain_uuid_list:
        start_domain(conn, uuid)


def batch_suspend_domains(conn: libvirt.virConnect, domain_uuid_list):
    '''batch suspend domains'''
    for uuid in domain_uuid_list:
        suspend_domain(conn, uuid)


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

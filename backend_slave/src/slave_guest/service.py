from src.domain_manager import guest as guest_manager
from src.domain_manager import device as device_manager
from src.utils import connect

connection = connect.get_libvirt_connection()

def create_domain(config_xml: str):
    return guest_manager.create_unpersistent_domain(connection, config_xml)

def shutdown_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.shutdown_domain(connection, uuid)

def destroy_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.destroy_domain(connection, uuid)

def start_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.start_domain(connection, uuid)

def reboot_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.restart_domain(connection, uuid)

def rename_domain(domain_name: str, new_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.rename_domain(connection, uuid, new_name)

def get_uuid_by_name(domain_name: str):
    return guest_manager.get_uuid_by_name(connection, domain_name)

def put_description(domain_name: str, description: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.set_domain_description(connection, uuid, description)

def delete_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.delete_domain(connection, uuid)

def pause_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.pause_domain(connection, uuid)

def resume_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.resume_domain(connection, uuid)

def set_auto_start_domain(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.set_auto_start(connection, uuid)

def batch_start_domains(domain_name_list):
    domain_uuid_list = []
    for name in domain_name_list:
        domain_uuid_list.add(guest_manager.get_uuid_by_name(name))
    return guest_manager.batch_start_domains(connection, domain_uuid_list)

def batch_pause_domains(domain_name_list):
    domain_uuid_list = []
    for name in domain_name_list:
        domain_uuid_list.add(guest_manager.get_uuid_by_name(name))
    return guest_manager.batch_pause_domains(connection, domain_uuid_list)

def batch_shutdown_domains(domain_name_list):
    domain_uuid_list = []
    for name in domain_name_list:
        domain_uuid_list.add(guest_manager.get_uuid_by_name(name))
    return guest_manager.batch_shutdown_domains(connection, domain_uuid_list)

def batch_delete_domains(domain_name_list):
    domain_uuid_list = []
    for name in domain_name_list:
        domain_uuid_list.add(guest_manager.get_uuid_by_name(name))
    return guest_manager.batch_delete_domains(connection, domain_uuid_list)

def batch_restart_domains(domain_name_list):
    domain_uuid_list = []
    for name in domain_name_list:
        domain_uuid_list.add(guest_manager.get_uuid_by_name(name))
    return guest_manager.batch_restart_domains(connection, domain_uuid_list)

def attach_device(domain_name: str, xml: str, flags: int = 0):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return device_manager.attach_device_to_domain(connection, uuid, xml, flags)

def detach_device(domain_name: str, xml: str, flags: int = 0):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return device_manager.detach_device_from_domain(connection, uuid, xml, flags)

def update_device(domain_name: str, xml: str, flags: int = 0):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return device_manager.update_domain_device(connection, uuid, xml, flags)

def set_domain_vcpu(domain_name: str, cpu_num: int, flags):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return device_manager.set_domain_vcpu(connection, uuid, cpu_num, flags)

def set_domain_memory(domain_name: str, memory_size: int, flags):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return device_manager.set_domain_memory(connection, uuid, memory_size, flags)

def monitor(domain_name: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.get_domain_monitor_status(connection, uuid)

def set_user_passwd(domain_name: str, user_name: str, passwd: str):
    uuid = guest_manager.get_uuid_by_name(connection, domain_name)
    return guest_manager.set_user_passwd(connection, uuid, user_name, passwd)

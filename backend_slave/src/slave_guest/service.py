from src.domain_manager import guest as guest_manager
from src.domain_manager import device as device_manager
from src.utils import connect

connection = connect.get_libvirt_connection()

def create_domain(config_xml: str):
    return guest_manager.create_persistent_domain(connection, config_xml)

def shutdown_domain(domain_uuid: str):
    return guest_manager.shutdown_domain(connection, domain_uuid)

def destroy_domain(domain_uuid: str):
    return guest_manager.destroy_domain(connection, domain_uuid)

def start_domain(domain_uuid: str):
    return guest_manager.start_domain(connection, domain_uuid)

def reboot_domain(domain_uuid: str):
    return guest_manager.restart_domain(connection, domain_uuid)

def rename_domain(domain_uuid: str, new_name: str):
    return guest_manager.rename_domain(connection, domain_uuid, new_name)

def get_uuid_by_name(domain_uuid: str):
    return guest_manager.get_uuid_by_name(connection, domain_uuid)

def put_description(domain_uuid: str, description: str):
    return guest_manager.set_domain_description(connection, domain_uuid, description)

def delete_domain(domain_uuid: str):   
    return guest_manager.delete_domain(connection, domain_uuid)

def pause_domain(domain_uuid: str):    
    return guest_manager.pause_domain(connection, domain_uuid)

def resume_domain(domain_uuid: str):
    return guest_manager.resume_domain(connection, domain_uuid)

def set_auto_start_domain(domain_uuid: str):    
    return guest_manager.set_auto_start(connection, domain_uuid)

def batch_start_domains(domain_uuid_list):
    return guest_manager.batch_start_domains(connection, domain_uuid_list)

def batch_pause_domains(domain_uuid_list):
    return guest_manager.batch_pause_domains(connection, domain_uuid_list)

def batch_shutdown_domains(domain_uuid_list):
    return guest_manager.batch_shutdown_domains(connection, domain_uuid_list)

def batch_delete_domains(domain_uuid_list):
    return guest_manager.batch_delete_domains(connection, domain_uuid_list)

def batch_restart_domains(domain_uuid_list):
    return guest_manager.batch_restart_domains(connection, domain_uuid_list)

def attach_device(domain_uuid: str, xml: str, flags: int = 0):
    return device_manager.attach_device_to_domain(connection, domain_uuid, xml, flags)

def detach_device(domain_uuid: str, xml: str, flags: int = 0):
    return device_manager.detach_device_from_domain(connection, domain_uuid, xml, flags)

def update_device(domain_uuid: str, xml: str, flags: int = 0):
    return device_manager.update_domain_device(connection, domain_uuid, xml, flags)

def set_domain_vcpu(domain_uuid: str, cpu_num: int, flags):
    return device_manager.set_domain_vcpu(connection, domain_uuid, cpu_num, flags)

def set_domain_memory(domain_uuid: str, memory_size: int, flags):
    return device_manager.set_domain_memory(connection, domain_uuid, memory_size, flags)

def monitor(domain_uuid: str):
    return guest_manager.get_domain_monitor_status(connection, domain_uuid)

def set_user_passwd(domain_uuid: str, user_name: str, passwd: str):
    return guest_manager.set_user_passwd(connection, domain_uuid, user_name, passwd)

def get_domain_interface_addresses(domain_uuid: str):
    return device_manager.get_domain_interface_addresses(connection, domain_uuid)

from src.volume.api import API
from src.guest.service import GuestService, SlaveService
from src.utils.response import APIResponse
import libvirt

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
guestService = GuestService()
slaveService = SlaveService()

class GuestAPI():

    def create_domain(self, domain_name: str, slave_name: str, **kwargs):
        return guestService.create_domain(domain_name, slave_name, **kwargs)

    def shutdown_domain(self, domain_name: str, slave_name: str):
        return guestService.shutdown_domain(domain_name, slave_name)

    def destroy_domain(self, domain_name: str, slave_name: str):
        return guestService.destroy_domain(domain_name, slave_name)

    def pause_domain(self, domain_name: str, slave_name: str):
        return guestService.pause_domain(domain_name, slave_name)(domain_name, slave_name)

    def resume_domain(self, domain_name: str, slave_name: str):
        return guestService.resume_domain(domain_name, slave_name)

    def start_domain(self, domain_name: str, slave_name: str):
        return guestService.start_domain(domain_name, slave_name)

    def batch_start_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_start_domains(domains_name_list, slave_name)

    def batch_pause_domains(self, domains_name_list, slave_name: str):

        return guestService.batch_pause_domains(domains_name_list, slave_name)
    
    def batch_shutdown_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_shutdown_domains(domains_name_list, slave_name)

    def batch_delete_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_delete_domains(domains_name_list, slave_name)

    def batch_restart_domains(self, domains_name_list, slave_name: str):
        return guestService.batch_restart_domains(domains_name_list, slave_name)

    def get_domains_list():
        return guestService.get_domains_list()

    def rename_domain(self, domain_name: str, new_name: str, slave_name: str):
        return guestService.rename_domain(domain_name, new_name, slave_name)

    def put_description(self, domain_name: str, new_description: str, slave_name: str):
        return guestService.put_description(domain_name, new_description, slave_name)

    def delete_domain(self, domain_name: str, slave_name: str):
        return guestService.delete_domain(domain_name, slave_name)
    
    def attach_nic(self, domain_name: str, slave_name: str, interface_name: str, flags: int):
        return guestService.attach_nic(domain_name, slave_name, interface_name, flags)
    
    def detach_nic(self, domain_name: str, slave_name: str, interface_name: str, flags: int):
        return guestService.detach_nic(domain_name, slave_name, interface_name, flags)
    
    def list_nic(self, domain_name: str, slave_name: str) -> APIResponse:
        return guestService.list_nic(domain_name, slave_name)
        
    def set_domain_vcpu(self, domain_name: str, slave_name: str, cpu_num: int, flags: int):
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.set_domain_vcpu(domain_name, slave_name, cpu_num, flags)
    
    def set_domain_memory(self, domain_name: str, slave_name: str, memory_size: int, flags: int):
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.set_domain_memory(domain_name, slave_name, memory_size, flags)
    
    def add_vnc(self, domain_name: str, slave_name: str, port:int, passwd: str, flags):
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.add_vnc(domain_name, slave_name, port, passwd, flags)
    
    def add_spice(self, domain_name: str, slave_name: str, port:int, passwd: str, flags):
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.add_spice(domain_name, slave_name, port, passwd, flags)
    
    def change_graphic_passwd(self, domain_name: str, slave_name: str, port:int, passwd: str, flags, vnc=True):
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.change_graphic_passwd(domain_name, slave_name, port, passwd, flags, vnc)
    
    def monitor(self, domain_name: str, slave_name: str):
        return guestService.monitor(domain_name, slave_name)
    
    def get_domain_slave_name(session, domain_uuid: str):
        return guestService.get_domain_slave_name(domain_uuid)
    
    def get_domain_status(session, domain_uuid: str):
        return guestService.get_domain_status(domain_uuid)
    
    

class SlaveAPI():
    
    def create_slave(self, slave_name: str, slave_address) -> APIResponse:
        return slaveService.create_slave(slave_name, slave_address)
    
    def get_slave_by_uuid(self, uuid: str) -> APIResponse:
        return slaveService.get_slave_by_uuid(uuid)
    
    def get_slave_by_name(self, name: str) -> APIResponse:
        return slaveService.get_slave_by_name(name)
    
    def get_slave_address_by_uuid(self, uuid: str) -> APIResponse:
        return slaveService.get_slave_address(uuid=uuid)
    
    def get_slave_address_by_name(self, name: str) -> APIResponse:
        return slaveService.get_slave_address(slave_name=name)

    
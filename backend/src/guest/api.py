from functools import wraps
from src.guest.service import GuestService, SlaveService
from src.utils.response import APIResponse
from src.utils.config import CONF
import libvirt
import inspect

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

err_code = {
    0:"param error"
}
guestService = GuestService()
slaveService = SlaveService()

def NOT_NULL(dict: dict):
    def check(func):
        sig = inspect.signature(func)
        parameters = sig.parameters  #参数列表的有序字典
        @wraps(func)
        def decorator(*args, **kwargs):
            flag =False
            str = ""
            for key in dict:
                if not key in parameters or parameters[key] is None:
                    flag = True
                    str = str + str(key)
            if flag:
                return APIResponse.error(code=0, msg="These params are None. " + str)
            return func(*args, **kwargs)
        return decorator
    return check

def TO_INT(list: list):
    def revert(func):
        # sig = inspect.signature(func)
        # parameters = sig.parameters  # 参数有序字典
        # arg_keys = tuple(parameters.keys())
        @wraps(func)
        def decorator(*args, **kwargs):
            for key in list:
                if kwargs[key] is not None:
                    kwargs[key] = int(kwargs[key])
            return func(*args, **kwargs)
        return decorator
    return revert


class GuestAPI():
    def create_domain(self, domain_name: str, slave_name: str, **kwargs) -> APIResponse:
        return guestService.create_domain(domain_name , slave_name, **kwargs)
    
    def get_domain_detail(self, domain_uuid: str) -> APIResponse:
        return guestService.get_domain_detail(domain_uuid)

    def shutdown_domain(self, domain_uuid: str) -> APIResponse:
        return guestService.shutdown_domain(domain_uuid)

    def destroy_domain(self, domain_uuid: str) -> APIResponse:
        return guestService.destroy_domain(domain_uuid)

    def pause_domain(self, domain_uuid: str) -> APIResponse:
        return guestService.pause_domain(domain_uuid)

    def resume_domain(self, domain_uuid: str) -> APIResponse:
        return guestService.resume_domain(domain_uuid)
    
    def reboot_domain(self, domain_uuid: str) -> APIResponse:
        return guestService.reboot_domain(domain_uuid)

    def start_domain(self, domain_uuid: str) -> APIResponse:
        return guestService.start_domain(domain_uuid)

    def batch_domains_detail(self, domains_uuid_list: str) -> APIResponse:
        return guestService.batch_domains_detail(domains_uuid_list)

    def batch_start_domains(self, domains_uuid_list ) -> APIResponse:
        return guestService.batch_start_domains(domains_uuid_list)

    def batch_pause_domains(self, domains_uuid_list ) -> APIResponse:
        return guestService.batch_pause_domains(domains_uuid_list)
    
    def batch_resume_domains(self, domains_uuid_list ) -> APIResponse:
        return guestService.batch_resume_domains(domains_uuid_list)
    
    def batch_shutdown_domains(self, domains_uuid_list ) -> APIResponse:
        return guestService.batch_shutdown_domains(domains_uuid_list)

    def batch_delete_domains(self, domains_uuid_list ) -> APIResponse:
        return guestService.batch_delete_domains(domains_uuid_list)

    def batch_restart_domains(self, domains_uuid_list ) -> APIResponse:
        return guestService.batch_restart_domains(domains_uuid_list)

    def get_domains_list(self) -> APIResponse:
        return guestService.get_domains_list()

    def rename_domain(self, domain_uuid: str, new_name: str) -> APIResponse:
        return guestService.rename_domain(domain_uuid, new_name)

    def put_description(self, domain_uuid: str, new_description: str) -> APIResponse:
        return guestService.put_description(domain_uuid, new_description)
    
    @TO_INT(list = ["flags"])
    def delete_domain(self, domain_uuid: str, flags: int) -> APIResponse:
        return guestService.delete_domain(domain_uuid, flags)
    
    @TO_INT(list = ["flags"])
    def attach_nic(self, domain_uuid: str , interface_name: str, flags: int)-> APIResponse:
        return guestService.attach_nic(domain_uuid, interface_name, flags)
    
    @TO_INT(list = ["flags"])    
    def detach_nic(self, domain_uuid: str , interface_name: str, flags: int)->APIResponse:
        return guestService.detach_nic(domain_uuid, interface_name, flags)
    
    def list_nic(self, domain_uuid: str) -> APIResponse:
        return guestService.list_nic(domain_uuid)

    @TO_INT(list = ["cpu_num", "flags"])        
    def set_domain_vcpu(self, domain_uuid: str , cpu_num: int, flags: int) -> APIResponse:
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.set_domain_vcpu(domain_uuid, cpu_num, flags)
    
    @TO_INT(list = ["memory_size", "flags"])    
    def set_domain_memory(self, domain_uuid: str , memory_size: int, flags: int) -> APIResponse:
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.set_domain_memory(domain_uuid, memory_size, flags)

    @TO_INT(list = ["flags"])    
    def add_vnc(self, domain_uuid: str , port:int, passwd: str, flags) -> APIResponse:
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.add_vnc(domain_uuid, port=port, passwd=passwd, flags=flags)
    
    @TO_INT(list = ["flags"])    
    def delete_vnc(self, domain_uuid: str, flags) -> APIResponse:
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.delete_vnc(domain_uuid, flags)
       
    def get_vnc_addr(self, domain_uuid: str) -> APIResponse:
        return guestService.get_vnc_addr(domain_uuid)
    

    @TO_INT(list = ["flags"])    
    def add_spice(self, domain_uuid: str , port:str, passwd: str, flags)-> APIResponse:
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.add_spice(domain_uuid, port, passwd, flags)

    @TO_INT(list = ["flags"])    
    def change_graphic_passwd(self, domain_uuid: str , port:str, passwd: str, flags, vnc=True) -> APIResponse:
        if (flags is None):
            flags = libvirt.VIR_DOMAIN_VCPU_CURRENT
        return guestService.change_graphic_passwd(domain_uuid, port, passwd, flags, vnc)
    
    def monitor(self, domain_uuid: str) -> APIResponse:
        return guestService.monitor(domain_uuid)
    
    def set_user_passwd(self, domain_uuid: str , user_name: str, passwd: str) -> APIResponse:
        return guestService.set_user_passwd(domain_uuid, user_name, passwd)
        
    def get_domain_slave_name(self, domain_uuid: str)-> APIResponse:
        return guestService.get_domain_slave_name(domain_uuid)
    
    def get_domain_status(self, domain_uuid: str) -> APIResponse:
        return guestService.get_domain_status(domain_uuid)

    def attach_disk(self,
                    guest_uuid: str,
                    volume_name: str,
                    size: int = 20*1024,
                    volume_uuid: str = None,
                    flags: int = libvirt.VIR_DOMAIN_AFFECT_CONFIG) -> APIResponse:
        if size is not None:
            size = int(size)
        return guestService.attach_disk_to_guest(guest_uuid, volume_name,
                                                 volume_uuid, size, flags)

    def detach_disk(self,
                    guest_uuid: str,
                    volume_uuid: str,
                    flags: int = libvirt.VIR_DOMAIN_AFFECT_CONFIG) -> APIResponse:
        return guestService.detach_disk_from_domain(guest_uuid, volume_uuid, flags)


class SlaveAPI():
    
    def create_slave(self, slave_name: str, slave_address) -> APIResponse:
        return slaveService.create_slave(slave_name, slave_address)
    
    def delete_slave(self, slave_name: str) -> APIResponse:
        return slaveService.delete_slave(slave_name=slave_name)
    
    def slave_detail(self, slave_name: str) -> APIResponse:
        return slaveService.slave_detail(slave_name=slave_name)
    
    def get_slave_by_uuid(self, uuid: str) -> APIResponse:
        return slaveService.get_slave_by_uuid(uuid)
    
    def get_slave_by_name(self, name: str) -> APIResponse:
        return slaveService.get_slave_by_name(name)
    
    def get_slave_address_by_uuid(self, uuid: str) -> APIResponse:
        return slaveService.get_slave_address(uuid=uuid)
    
    def get_slave_address_by_name(self, name: str) -> APIResponse:
        return slaveService.get_slave_address(slave_name=name)
    
    def init_slave_db(self) -> APIResponse:
        return slaveService.init_slave_db()
    
    def get_slave_guests(self, name: str) -> APIResponse:
        return slaveService.get_slave_guests(name=name)
    
    def get_slave_status(self, slave_name) -> APIResponse:
        return slaveService.get_slave_status(slave_name)

    def get_all_slave_status(self) -> APIResponse:
        return slaveService.get_all_slave_status()
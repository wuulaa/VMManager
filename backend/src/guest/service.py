from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.guest.db.models import Guest
import src.volume.db as db

@singleton
class GuestService():
    @enginefacade.transactional
    def create_guest(self, session, uuid: str, name: str, slave_name: str, **kwargs):
        title = kwargs.get("title", None)
        description = kwargs.get("description", None)
        status = kwargs.get("status", None)
        architecture = kwargs.get("architecture", None)
        cpu = kwargs.get("cpu", None)
        max_cpu = kwargs.get("max_cpu", None)
        memory = kwargs.get("memory", None)
        max_memory = kwargs.get("max_memory", None)
        boot_option = kwargs.get("boot_option", None)
        spice_address = kwargs.get("spice_address", None)
        vnc_address = kwargs.get("vnc_address", None)
        parent_uuid = kwargs.get("parent_uuid", None)
        children_list = kwargs.get("children_list", None)
        backups_list = kwargs.get("backups_list", None)
        guest = Guest(uuid ,name, slave_name, title, description, status, architecture, cpu, max_cpu,
                      memory, max_memory, boot_option, spice_address, vnc_address, parent_uuid,
                      children_list, backups_list)
        db.insert(session, guest)
        return guest
    
    @enginefacade.transactional
    def status_update(self, session, uuid: str, status: str):
        db.condition_update(session, uuid, {"status": status})
        guest: Guest = db.select_by_uuid(session, Guest, uuid)
        return guest
    
    @enginefacade.transactional
    def get_uuid_by_name(domain_name: str, slave_name: str):
        return db.condition_select(Guest, values = {"name": domain_name, "slave_name": slave_name}).uuid
    

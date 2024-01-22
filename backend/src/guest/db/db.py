from src.utils.sqlalchemy import enginefacade
from src.guest.db.models import Guest, Slave
import src.volume.db as db

@enginefacade.auto_session
def create_guest(session, uuid: str, name: str, slave_name: str, **kwargs):
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
    guest = Guest(uuid, name, slave_name)
    db.insert(session, guest)
    return guest

@enginefacade.auto_session
def update_guest(session, uuid: str, values: dict):
    return db.condition_update(session, Guest, uuid, values)

@enginefacade.auto_session
def status_update(session, uuid: str, status: str):
    db.condition_update(session, uuid, {"status": status})
    guest: Guest = db.select_by_uuid(session, Guest, uuid)
    return guest

@enginefacade.auto_session
def get_domain_uuid_by_name(session, domain_name: str, slave_name: str):
    return db.condition_select(session, Guest, values = {"name": domain_name, "slave_name": slave_name}).uuid

@enginefacade.auto_session
def get_domain_list(session):
    return db.condition_select(session, Guest)

@enginefacade.auto_session
def delete_domain_by_uuid(session, uuid: str):
    guest = db.select_by_uuid(session, Guest, uuid)
    return db.delete(session, guest)

@enginefacade.auto_session
def get_domain_slave_name(session, domain_uuid: str):
    guest: Guest = db.select_by_uuid(session, domain_uuid)
    return guest.slave_name

@enginefacade.auto_session
def get_domain_status(session, domain_uuid: str):
    guest: Guest = db.select_by_uuid(session, domain_uuid)
    return guest.status

    
@enginefacade.auto_session
def create_slave(session, name: str, address: str):
    slave = Slave(name, address)
    db.insert(session, slave)
    return slave


@enginefacade.auto_session
def delete_slave(session, name: str):
    slave = db.select_by_name(session, Slave, name)
    return db.delete(session, slave)


@enginefacade.auto_session
def get_slave_guests(session, name: str):
    guests: list[Guest] = db.condition_select(session, Guest, values={"slave_name": name})
    return guests


@enginefacade.auto_session
def get_slave_by_uuid(session, uuid: str):
    slave: Slave = db.select_by_uuid(session, Slave, uuid)
    return slave

@enginefacade.auto_session
def get_slave_by_name(session, name: str):
    slave: Slave = db.select_by_name(session, Slave, name)
    return slave

@enginefacade.auto_session
def get_slave_uuid_by_name(session, name: str):
    slave: Slave = db.select_by_name(session, Slave, name)
    return slave.uuid

@enginefacade.auto_session
def get_slave_name_by_uuid(session, uuid: str):
    slave: Slave = db.select_by_uuid(session, Slave, uuid)
    return slave.name

@enginefacade.auto_session
def get_slave_address_by_uuid(session, uuid: str):
    slave: Slave = db.select_by_uuid(session, Slave, uuid)
    return slave.address

    

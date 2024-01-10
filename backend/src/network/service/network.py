from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.network.db.models import Interface, Network
from src.utils.sqlalchemy import api as db

@singleton
class InterfaceService():
    @enginefacade.transactional
    def create_interface(self, session,
                        name: str,
                        network_name: str,
                        ip_address: str,
                        mac: str = None,
                        inerface_type: str = "direct"
                       ):
        network_uuid = db.select_by_name(session, Network, network_name).uuid
        interface = Interface(name, network_uuid, ip_address,
                              mac, inerface_type)
        db.insert(session, interface)
        return interface 
    
    @enginefacade.transactional
    def delete_interface(self, session,
                       uuid: str):
        interface = db.select_by_uuid(session, Interface, uuid)
        db.delete(session, interface)
    
    @enginefacade.transactional
    def batch_delete_interface(self, session, interfaces):
        db.batch_delete(session, interfaces)
    
    @enginefacade.transactional
    def get_interface_by_uuid(self, session, uuid):
        return db.select_by_uuid(session, Interface, uuid)
    
    @enginefacade.transactional
    def update_interface_ip(self, session, uuid, new_ip):
        db.condition_update(session, Interface, uuid, {"ip_address": new_ip})
        return db.select_by_uuid(session, Interface, uuid)
    
    @enginefacade.transactional
    def update_interface_mac(self, session, uuid, mac):
        db.condition_update(session, Interface, uuid, {"mac": mac})
        return db.select_by_uuid(session, Interface, uuid)
    
    @enginefacade.transactional
    def update_interface_port(self, session, uuid, port_uuid):
        db.condition_update(session, Interface, uuid, {"port_uuid": port_uuid})
        return db.select_by_uuid(session, Interface, uuid)
    
    
@singleton
class NetworkService():
    @enginefacade.transactional
    def create_network(self, session,
                       name: str,
                       ip_address: str):
        network = Network(name, ip_address)
        db.insert(session, network)
        return network
    
    @enginefacade.transactional
    def delete_network_by_uuid(self, session,
                       uuid: str):
        network = db.select_by_uuid(session, Network, uuid)
        db.delete(session, network)
        
    @enginefacade.transactional
    def delete_network_by_name(self, session,
                       name: str):
        network = db.select_by_name(session, Network, name)
        db.delete(session, network)
    
    @enginefacade.transactional
    def get_network_by_uuid(self, session, uuid):
        return db.select_by_uuid(session, Network, uuid)
    
    @enginefacade.transactional
    def get_network_by_name(self, session, name):
        return db.select_by_name(session, Network, name)
    
    @enginefacade.transactional
    def get_network_uuid_by_name(self, session, name):
        network: Network = db.select_by_name(session, Network, name)
        return network.uuid
    
    
        
    
    

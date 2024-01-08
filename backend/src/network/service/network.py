from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.network.db.models import Interface, Network
from src.utils.sqlalchemy import api as db

@singleton
class InterfaceService():
    @enginefacade.transactional
    def create_interface(self, session,
                       network_uuid: str,
                       port_uuid: str,
                       ip_address: str,
                       mac: str = None,
                       inerface_type: str = "direct"
                       ):
        interface = Interface(network_uuid, port_uuid, ip_address,
                              mac, inerface_type)
        db.insert(session, interface)
        return interface
    
    @enginefacade.transactional
    def delete_interface(self, session,
                       uuid: str):
        interface = db.select_by_uuid(session, Interface, uuid)
        db.delete(session, interface)
    
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
    def update_interface_network(self, session, uuid, network_uuid):
        db.condition_update(session, Interface, uuid, {"network_uuid": network_uuid})
        return db.select_by_uuid(session, Interface, uuid)
    

class NetworkService():
    @enginefacade.transactional
    def create_network(self, session,
                       name: str,
                       ip_address: str):
        network = Network(name, ip_address)
        db.insert(session, network)
        return network
    
    @enginefacade.transactional
    def delete_network(self, session,
                       uuid: str):
        network = db.select_by_uuid(session, Network, uuid)
        db.delete(session, network)
    
    @enginefacade.transactional
    def get_network_by_uuid(self, session, uuid):
        return db.select_by_uuid(session, Network, uuid)
    
        
    
    

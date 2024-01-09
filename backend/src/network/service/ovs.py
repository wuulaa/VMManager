from src.utils.singleton import singleton
from src.utils.sqlalchemy import enginefacade
from src.network.db.models import OVSBridge, OVSPort
from src.guest.db.models import Guest, Slave
from src.utils.sqlalchemy import api as db

@singleton
class OVSService():
    
    ############
    ## bridge ##
    ############
    
    @enginefacade.transactional
    def create_bridge(self, session,
                      bridge_name: str,
                      slave_uuid: str
                      ):
        bridge = OVSBridge(bridge_name, slave_uuid)
        db.insert(session, bridge)
        return bridge
    
    @enginefacade.transactional
    def delete_bridge(self, session,
                      bridge_uuid: str
                      ):
        bridge = db.select_by_uuid(session, OVSBridge, bridge_uuid)
        db.delete(session, bridge)
    
    
    @enginefacade.transactional
    def get_bridge_by_uuid(self, session,
                              bridge_uuid: str
                              ):
        bridge = db.select_by_uuid(session, OVSBridge, bridge_uuid)
        return bridge
    
    @enginefacade.transactional
    def get_bridge_by_name(self, session,
                           bridge_name: str
                           ):
        bridge = db.select_by_name(session, OVSBridge, bridge_name)
        return bridge
    
    
    @enginefacade.transactional
    def get_bridge_uuid_by_name(self, session,
                           bridge_name: str
                           ):
        bridge = db.select_by_name(session, OVSBridge, bridge_name)
        return bridge.uuid
    
    ##########
    ## port ##
    ##########
    
    @enginefacade.transactional
    def create_port(self, session,
                    name: str,
                    bridge_uuid: str,
                    port_type: str = "internal",
                    remote_ip: str= None,
                    vlan_tag: str = None
                    ):
        bridge: OVSBridge = db.select_by_uuid(session, OVSBridge, bridge_uuid)
        port = OVSPort(name, bridge_uuid, port_type, remote_ip, vlan_tag)
        port.slave_uuid = bridge.slave_uuid
        db.insert(session, port)
        return port
    
    @enginefacade.transactional
    def get_port_by_uuid(self, session,port_uuid: str):
        port = db.select_by_uuid(session, OVSPort, port_uuid)
        return port
    
    @enginefacade.transactional
    def get_port_by_name(self, session, port_name: str):
        port = db.select_by_name(session, OVSPort, port_name)
        return port
    
    @enginefacade.transactional
    def delete_port(self, session,
                    port_uuid: str
                    ):
        port = db.select_by_uuid(session, OVSPort, port_uuid)
        db.delete(session, port)
        
    @enginefacade.transactional
    def set_port_tag(self, session,
                     port_uuid: str,
                     tag: str
                     ):
        db.condition_update(session, OVSPort, port_uuid, {"vlan_tag": tag})
        port: OVSPort = db.select_by_uuid(session, OVSPort, port_uuid)
        return port
    
    
        
    
 
    
        
    
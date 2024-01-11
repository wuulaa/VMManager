import requests
from src.utils.response import APIResponse
from src.utils.singleton import singleton
from src.domain_xml.device import interface
from src.common.network_manager import api as netapi
from src.guest.db.models import Slave
from src.guest.service import SlaveService
from src.network.db.models import Network, Interface, OVSPort
from src.network import db 
from src.utils.sqlalchemy import enginefacade
from src.utils.config import CONF
from src.utils import consts


@singleton
class NetworkService:
    
    @enginefacade.transactional
    def create_top_network(self, session,
                           network_address: str):
        '''
        This is an initial function which creates top level network.
        All ovs bridges are created in master and slaves.
        Vxlan ports are set so that master and slave could be connected.
        NAT network using iptables is set in master node, 
        so that Internet could be accessed via master node. 
        '''
        # TODO: should write db?
        
        slave_count: int = CONF.getint("slaves", "slaveCount")
        bridge_prefix: str = CONF.get("network", "bridge_prefix")
        master_ip: str = CONF.get("master", "master").split(":")[0]
        
        master_bridge_name = bridge_prefix + "_center"
        slave_bridge_name = bridge_prefix + "_slave"
        
        # 1. create master bridge and nat network
        netapi.create_bridge(bridge_name=master_bridge_name)
        netapi.create_ovs_nat_network(network_address, master_bridge_name)
        netapi.init_iptables()

        # 2. create slave bridges and add vxlan ports
        for i in range(1, slave_count + 1):
            slave_address: str = CONF.get("slaves", f"slave{i}")
            slave_ip: str = slave_address.split(":")[0]
            url = "http://"+ slave_address
            
            data = {
                consts.P_BRIDGE_NAME: slave_bridge_name
            }
            response = requests.post(url + "/createBridge/", data)
            
            data = {
                consts.P_BRIDGE_NAME: slave_bridge_name,
                consts.P_PORT_NAME: "vxlan",
                consts.P_REMOTE_IP: master_ip
            }
            response = APIResponse(requests.post(url + "/addVxlanPort/", data))
            netapi.add_vxlan_port_to_bridge(master_bridge_name, f"vxlan_{i}", slave_ip)
        
        return APIResponse.success()
    
    
    @enginefacade.transactional
    def create_interface(self, session,
                         name: str,
                         network_name: str,
                         ip_address: str,
                         mac: str = None,
                         inerface_type: str = "direct"):
        """
        create virtual interface.
        this is a purely db function,
        real port is set during binding
        """
        
        # write interface db
        network = db.get_network_by_name(network_name)
        if network is None:
            raise Exception(f'cannot find a network which name={name}')
        interface: Interface = db.create_interface(name=name,
                                           network_name=network_name,
                                           ip_address=ip_address,
                                           mac=mac,
                                           inerface_type=inerface_type
                                           )
        uuid = interface.uuid
        return APIResponse.success(data={"interface_uuid": uuid})
        
    
    @enginefacade.transactional
    def bind_interface_to_port(self, session, interface_uuid: str, slave_name: str):
        """
        create real ovs port in slave and bind it to a interface

        Args:
            interface_uuid (str): interface uuid
            slave_name (str): slave node name
        """
        interface: Interface = db.get_interface_by_uuid(interface_uuid)
        name: str = interface.name
        
        # 1. create ovs port in slave
        slave_address: str = CONF.get("slaves", slave_name)
        slave_bridge_name = CONF.get("network", "bridge_prefix") + "_slave"
        
        url = "http://"+ slave_address
        
        # add real port
        data = {
                consts.P_BRIDGE_NAME: slave_bridge_name,
                consts.P_PORT_NAME: name,
                consts.P_TYPE: "internal"
            }
        response: requests.Response = requests.post(url + "/addPort/", data)
        
        # 2. create port in db
        port: OVSPort = db.create_port(session, name, interface_uuid, "internal")
        port_uuid = port.uuid
        
        # 3. set interface slave uuid, port uuid and status in db. TODO: slave uuid
        db.update_interface_port(session, interface_uuid, port_uuid)
        db.update_interface_status(session, interface_uuid, "bound_unuse")
        
        
    def unbind_interface_port(self, session, interface_uuid: str):
        """
        unbind ovs port and interface,
        port is directly removed 

        """
        interface: Interface = db.get_interface_by_uuid(interface_uuid)
        name: str = interface.name
        
        pass
        
        
    def delete_interface(self, session, uuid: str, name: str=None):
        pass
    
    
    def create_network(self, session, name, ip_address):
        """
        create virtual network,
        this only needs to write db
        
        Args:
            name (str): name of the network
            ip_address (str): address of the network, eg: 1.2.3.4/24
        """
        db.create_network(name=name, ip_address=ip_address)
    
    
    @enginefacade.transactional
    def delete_network(self, session, name):
        """
        delete virtual network,
        all virtual interfaces of the network would also be deleted

        Args:
            name (str): network name
        """
        network: Network = db.get_network_by_name(name)
        if network is None:
            raise Exception(f'cannot find a network which name={name}')
        interfaces: list[Interface] = network.interfaces
        for interface in interfaces:
            self.unbind_interface_port(session=session, interface_uuid=interface.uuid)
            self.delete_interface(session, interface.uuid)
        db.delete_network_by_name(session, name)
    
    
    def create_network_routing(self, session, addrA, addrB, parent_addr):
        # TODO: db
        netapi.create_route(addrA, addrB, parent_addr)
    
    
    def delete_network_routing(self, session, addrA, addrB, parent_addr):
        # TODO: db
        netapi.delete_route(addrA, addrB, parent_addr)
    
    
    def get_interface_xml(self, session):
        pass
    
    
    def add_interface_to_domain(self, session):
        pass
    
    
    def remove_interface_to_domain(self,session):
        pass
    
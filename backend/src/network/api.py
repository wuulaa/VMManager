import requests
from utils.response import APIResponse
from domain_xml.device import interface
from backend.src.common.network_manager import api as netapi
from src.guest.db.models import Slave
from src.guest.service import SlaveService
from src.network.db.models import Network, Interface
from src.network.service.network import NetworkService, InterfaceService, db
from src.network.service.ovs import OVSService, OVSPort
from src.utils.sqlalchemy import enginefacade
from src.utils.config import CONF
from src.utils import consts


# def create_interface():
#     '''create default libvirt interface'''
#     try:
#         interface_builder: interface.DeviceInterface = interface.create_default_interface_builder()
#         xml_string = interface_builder.get_xml_string()
#         APIResponse.success(xml_string)
#     except Exception as err:
#         APIResponse.error(code=400, msg=str(err))
network_service = NetworkService()
interface_service = InterfaceService()
ovs_service = OVSService()
slave_service = SlaveService()
    
class NetworkAPI:
    
    @enginefacade.transactional
    def create_top_network(self,
                           network_address: str):
        '''
        This is an initial function which creates top level network.
        All ovs bridges are created in master and slaves.
        Vxlan ports are set so that master and slave could be connected.
        NAT network using iptables is set in master node, 
        so that Internet could be accessed via master node. 
        '''
        # TODO: db
        
        slave_count: int = CONF.getint("slaves", "slaveCount")
        bridge_prefix: str = CONF.get("network", "bridge_prefix")
        master_ip: str = CONF.get("master", "master").split(":")[0]
        
        master_bridge_name = bridge_prefix + "_center"
        slave_bridge_name = bridge_prefix + "_slave"
        
        # create master bridge and nat network
        netapi.create_bridge(bridge_name=master_bridge_name)
        netapi.create_ovs_nat_network(network_address, master_bridge_name)
        netapi.init_iptables()

        # create bridge and add vxlan ports
        for i in range(1, slave_count + 1):
            slave_address: str = CONF.get("slaves", f"slave{i}")
            slave_ip: str = slave_address.split(":")[0]
            url = "http://"+ slave_address
            
            data = {
                consts.P_BRIDGE_NAME: slave_bridge_name
            }
            response: requests.Response = requests.post(url + "/createBridge/", data)
            
            slave_uuid = slave_service.get_uuid_by_name(name=f"slave{i}")
            ovs_service.create_bridge(bridge_name=slave_bridge_name,
                                      slave_uuid=slave_uuid)
            
            # vxlan ports not stored in db ?
            data = {
                consts.P_BRIDGE_NAME: slave_bridge_name,
                consts.P_PORT_NAME: "vxlan",
                consts.P_REMOTE_IP: master_ip
            }
            response: requests.Response = requests.post(url + "/addVxlanPort/", data)
            netapi.add_vxlan_port_to_bridge(master_bridge_name, f"vxlan_{i}", slave_ip)
        
           
    @enginefacade.transactional
    def create_interface(self,
                         name: str,
                         network_name: str,
                         ip_address: str,
                         slave_name: str,
                         mac: str = None,
                         inerface_type: str = "direct"):
        """
        create virtual interface.
        ovs port is also created in the given slave
        """
        #TODO: set this in db?
        slave_address: str = CONF.get("slaves", slave_name)
        
        bridge_prefix: str = CONF.get("network", "bridge_prefix")
        slave_bridge_name = bridge_prefix + "_slave"
        bridge_uuid = ovs_service.get_bridge_uuid_by_name(slave_bridge_name)
        url = "http://"+ slave_address
        
        # add real port
        data = {
                consts.P_BRIDGE_NAME: slave_bridge_name,
                consts.P_PORT_NAME: name,
                consts.P_TYPE: "internal"
            }
        response: requests.Response = requests.post(url + "/addPort/", data)
        
        # write ovs db TODO: vlan tag?
        port: OVSPort = ovs_service.create_port(name=name,
                                                bridge_uuid=bridge_uuid,
                                                )
        
        # write interface db
        network = network_service.get_network_by_name(network_name)
        if network is None:
            raise Exception(f'cannot find a network which name={name}')
        interface: Interface = interface_service.create_interface(name=name,
                                           network_name=network_name,
                                           ip_address=ip_address,
                                           mac=mac,
                                           inerface_type=inerface_type
                                           )
        interface_service.update_interface_port(uuid=interface.uuid,
                                                port_uuid=port.uuid)
        
        #TODO: should interface also have a slave_uuid?
        
    
    def delete_interface(self):
        pass
    
    def create_network(self, name, ip_address):
        """
        create virtual network,
        this only needs to write db
        

        Args:
            name (str): name of the network
            ip_address (str): address of the network, eg: 1.2.3.4/24
        """
        network_service.create_network(name=name, ip_address=ip_address)
    
    @enginefacade.transactional
    def delete_network(self, name):
        network: Network = network_service.get_network_by_name(name)
        if network is None:
            raise Exception(f'cannot find a network which name={name}')
        interfaces: list[Interface] = network.interfaces
        interface_service.batch_delete_interface(interfaces=interfaces)
        network_service.delete_network_by_name(name=name)
    
    
    def create_network_routing(self, addrA, addrB, parent_addr):
        # TODO: db
        netapi.create_route(addrA, addrB, parent_addr)
    
    
    def delete_network_routing(self, addrA, addrB, parent_addr):
        # TODO: db
        netapi.delete_route(addrA, addrB, parent_addr)
    
    
    def get_interface_xml(self):
        pass
    
    
    def add_interface_to_domain(self):
        pass
    
    
    def remove_interface_to_domain(self):
        pass
    
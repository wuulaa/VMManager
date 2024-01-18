import requests
import ipaddress
from src.utils.response import APIResponse
from src.utils.singleton import singleton
from src.domain_xml.device import interface as interface_xml
from src.common.network_manager import api as netapi
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
        All related ovs bridges are created in master and slaves.
        Vxlan ports are set so that master and slave could be connected.
        NAT network using iptables is set in master node, 
        so that Internet could be accessed via master node. 
        '''
        # TODO: should write db?
        try:
            slave_count: int = CONF.getint("slaves", "slaveCount")
            bridge_prefix: str = CONF.get("network", "bridge_prefix")
            master_ip: str = CONF.get("master", "master").split(":")[0]
            
            master_bridge_name = bridge_prefix + "_master"
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
                response1 = requests.post(url + "/createBridge", data)
                
                # master and slave cannot use the same remote ip
                data = {
                    consts.P_BRIDGE_NAME: slave_bridge_name,
                    consts.P_PORT_NAME: f"vxlan_slave_{i}",
                    consts.P_REMOTE_IP: master_ip
                }
                response2 = APIResponse(requests.post(url + "/addVxlanPort", data))
                
                netapi.add_vxlan_port_to_bridge(master_bridge_name, f"vxlan_master_{i}", slave_ip)
                
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    
    @enginefacade.transactional
    def delete_top_network(self, session,
                           network_address: str):
        '''
        This is an destruction function which destroys top level network.
        All related ovs bridges are destroyed in master and slaves.
        NAT network using iptables is removed in master node, 
        '''
        try:
            slave_count: int = CONF.getint("slaves", "slaveCount")
            bridge_prefix: str = CONF.get("network", "bridge_prefix")
            master_ip: str = CONF.get("master", "master").split(":")[0]
            
            master_bridge_name = bridge_prefix + "_master"
            slave_bridge_name = bridge_prefix + "_slave"
            
            # 1. delete master bridge and nat network
            netapi.delete_bridge(bridge_name=master_bridge_name)
            netapi.delete_ovs_nat_network(network_address)
            netapi.uninit_iptables()

            # 2. delete slave bridges
            for i in range(1, slave_count + 1):
                slave_address: str = CONF.get("slaves", f"slave{i}")
                url = "http://"+ slave_address
                
                data = {
                    consts.P_BRIDGE_NAME: slave_bridge_name
                }
                response = requests.post(url + "/deleteBridge", data)
                
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def create_interface(self, session,
                         name: str,
                         network_name: str,
                         ip_address: str,
                         gateway: str, 
                         mac: str = None,
                         inerface_type: str = "direct"):
        """
        create virtual interface.
        this is a purely db function,
        real port is set during binding
        """
        
        # write interface db
        network: Network = db.get_network_by_name(session, network_name)
        if network is None:
            return APIResponse.error(400, f'cannot find a network which name={name}')
        
        if not is_ip_in_network(ip_address, network.address):
            return APIResponse.error(400, f'interface address is not within network')
        
        try:
            interface: Interface = db.create_interface(session,
                                            name=name,
                                            network_name=network_name,
                                            ip_address=ip_address,
                                            gateway=gateway,
                                            mac=mac,
                                            inerface_type=inerface_type
                                            )
            uuid = interface.uuid
            return APIResponse.success(data={"interface_uuid": uuid})
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    
    @enginefacade.transactional
    def bind_interface_to_port(self, session, interface_uuid: str, slave_name: str):
        """
        create real ovs port in slave and bind it to a interface

        Args:
            interface_uuid (str): interface uuid
            slave_name (str): slave node name
        """
        try:
            interface: Interface = db.get_interface_by_uuid(session, interface_uuid)
            name: str = interface.name
            
            from src.guest.api import SlaveAPI, GuestAPI
            slave_api = SlaveAPI()
            guest_api = GuestAPI()
            
            # 1. create ovs port in slave
            slave_address: str = slave_api.get_slave_address_by_name(slave_name).get_data()
            slave_uuid: str = slave_api.get_slave_by_name(name).get_data().uuid
            slave_bridge_name = CONF.get("network", "bridge_prefix") + "_slave"
            
            url = "http://"+ slave_address
            
            # add real port
            data = {
                    consts.P_BRIDGE_NAME: slave_bridge_name,
                    consts.P_PORT_NAME: name,
                    consts.P_TYPE: "internal"
                }
            response: requests.Response = requests.post(url + "/addPort/", data)
            
            # generate interface xml
            mac = interface.mac
            xml = interface_xml.create_direct_ovs_interface(name, mac).get_xml_string()
            
            # 2. create port in db
            port: OVSPort = db.create_port(session, name, interface_uuid, "internal")
            port_uuid = port.uuid
            
            # 3. set interface slave uuid, port uuid, xml and status in db.
            db.update_interface_port(session, interface_uuid, port_uuid)
            db.update_interface_status(session, interface_uuid, "bound_unuse")
            db.update_interface_slave_uuid(session, interface_uuid, slave_uuid)
            db.update_interface_xml(session, interface_uuid, xml)
            
            return APIResponse.success()
        
        except Exception as e:
            raise e
        
        
    @enginefacade.transactional
    def unbind_interface_port(self, session, interface_uuid: str):
        """
        unbind ovs port and interface,
        port is directly deleted

        """
        from src.guest.api import SlaveAPI, GuestAPI
        slave_api = SlaveAPI()
        guest_api = GuestAPI()
        
        try:
            interface: Interface = db.get_interface_by_uuid(session, interface_uuid)
            port_name: str = interface.name
            slave_address: str = slave_api.get_slave_address_by_uuid(interface.slave_uuid).get_data()
            url = "http://"+ slave_address
            slave_bridge_name = CONF.get("network", "bridge_prefix") + "_slave"
            
            # 1. delete ovs-port in slave
            data = {
                    consts.P_BRIDGE_NAME: slave_bridge_name,
                    consts.P_PORT_NAME: port_name,
                }
            response: requests.Response = requests.post(url + "/delPort/", data)
            
            # 2. write port db
            db.delete_port(session, interface.port_uuid)
            
            # 3. write interface db
            db.update_interface_port(session, interface_uuid, None)
            db.update_interface_status(session, interface_uuid, "un_bound")
            db.update_interface_slave_uuid(session, interface_uuid, None)
            db.update_interface_xml(session, interface_uuid, None)
            
            return APIResponse.success()
        except Exception as e:
            raise e
        
        
    @enginefacade.transactional
    def delete_interface(self, session, interface_uuid: str=None, name: str = None):
        try:
            if interface_uuid:
                interface: Interface = db.get_interface_by_uuid(session, interface_uuid)
            elif name:
                interface: Interface = db.get_interface_by_name(session, name)
                
        
            if interface is None:
                return APIResponse.error(code=400, msg=f'cannot find a interface which name={name}, uuid={interface_uuid}')
            
            interface_uuid = interface.uuid
            
            # 1. in bound unbound the interace
            if interface.status != "unbound":
                self.unbind_interface_port(session, interface_uuid)
            
            # 2. delete in db
            db.delete_interface_by_uuid(session, interface_uuid)
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def modify_interface(self, session, interface_uuid: str = None, name: str = None, ip_addr: str = None, gateway:str =None):
        """
        modify interface, currently supports ip and gateway only,
        make sure to pass them both
        """
        from src.guest.api import GuestAPI
        guest_api = GuestAPI()
        
        try:
            if interface_uuid:
                interface: Interface = db.get_interface_by_uuid(session, interface_uuid)
            elif name:
                interface: Interface = db.get_interface_by_name(session, name)
                
            if interface is None:
                return APIResponse.error(code=400, msg=f'cannot find a interface which name={name}, uuid = {interface_uuid}')
            
            remove_domain_ip = False
            if gateway is None and ip_addr is None:
                remove_domain_ip = True
            else:
                if gateway is None:
                    gateway = interface.gateway
                if ip_addr is None:
                    ip_addr = interface.ip_address
                
            # 1. update in db
            db.update_interface_ip(session, interface.uuid, ip_addr)
            db.update_interface_gateway(session, interface.uuid, gateway)
            # 2. check if is used in domain
            if interface.guest_uuid is not None:
                    
                domain_status = guest_api.get_domain_status(interface.guest_uuid).get_data()
            
                if domain_status == 1:
                    # if domain is running, directly change the ip/gateway
                    self.set_domain_ip(session, interface.guest_uuid,
                                    interface.name, ip_addr, gateway, remove_domain_ip)
                else:
                    # else set interface as modified, ip change would apply after starting domain
                    db.update_interface_modified(session, interface.uuid, True)
                    
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def domain_ip_modified(self, session, domain_uuid):
        """
        Determine whether domain's interface ip is modified when domain is not running.
        This function should be called only when staring the domain.
        If modified, call funcs to change domain's static ip after starting the domain.
        This function should be called after starting domain

        """
        # find domain's interfaces
        interfaces: list[Interface] = db.condition_select(session, Interface, values={"guest_uuid" : domain_uuid})
        for interface in interfaces:
            if interface.ip_modified:
                # if interface is modified, change domain static ip
                addr = interface.ip_address
                gateway = interface.gateway
                if addr or gateway:
                    self.set_domain_ip(session, domain_uuid, interface.name, addr, gateway, False)
                else:
                    # if gateway and ip are both None, do remove static ip
                    self.set_domain_ip(session, domain_uuid, interface.name, None, None, True)
                db.update_interface_modified(session, interface.uuid, False)
        return APIResponse.success()
    
    
    @enginefacade.transactional
    def create_network(self, session, name, ip_address):
        """
        create virtual network,
        this only needs to write db
        
        Args:
            name (str): name of the network
            ip_address (str): address of the network, eg: 1.2.3.4/24
        """
        try:
            network: Network = db.create_network(session, name=name, ip_address=ip_address)
            return APIResponse.success(network.uuid)
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def delete_network(self, session, name):
        """
        delete virtual network,
        all virtual interfaces of the network would also be deleted

        Args:
            name (str): network name
        """
        try:
            network: Network = db.get_network_by_name(session, name)
            if network is None:
                return APIResponse.error(code=400, msg=f'cannot find a network which name={name}')
            interfaces: list[Interface] = network.interfaces
            for interface in interfaces:
                self.delete_interface(session, interface.uuid)
            db.delete_network_by_name(session, name)
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    def create_network_routing(self, session, addrA, addrB, parent_addr):
        # TODO: db
        netapi.create_route(addrA, addrB, parent_addr)
    
    
    def delete_network_routing(self, session, addrA, addrB, parent_addr):
        # TODO: db
        netapi.delete_route(addrA, addrB, parent_addr)
    
    
    @enginefacade.transactional
    def get_interface_xml(self, session, name: str):
        interface: Interface = db.get_interface_by_name(session, name)
        if interface is None:
            return APIResponse.error(400, f"cannot find interface with name = {name}")
        return APIResponse.success(interface.xml)
        
        
    @enginefacade.transactional
    def add_interface_to_domain(self, session, interface_name: str, domain_uuid: str):
        """
        add interface to domain.
        this only includes db and bind operation, ip is not really set.
        Note that domain ip could be acutally set when domain is running.
        """
        from src.guest.api import GuestAPI
        guest_api = GuestAPI()
        
        try:
            interface: Interface = db.get_interface_by_name(session, interface_name)
            if interface.status == "bound_in_use" or interface.guest_uuid is not None:
                return APIResponse.error(401, "interface already in use")
            slave_name = guest_api.get_domain_slave_name(domain_uuid)
            
            self.bind_interface_to_port(session, interface.uuid, slave_name)
            db.update_interface_guest_uuid(session, interface.uuid, domain_uuid)
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    
    @enginefacade.transactional
    def remove_interface_from_domain(self, session, interface_name, domain_uuid):
        """
        remove interface from domain.
        this only includes interface db and unbind operations.

        """
        try:
            interface: Interface = db.get_interface_by_name(session, interface_name)
            if interface.status != "bound_in_use" or interface.guest_uuid is None:
                return APIResponse.error(401, "interface not used by domain")
            self.unbind_interface_port(session, interface.uuid)
            db.update_interface_guest_uuid(session, interface.uuid, None)
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    def set_domain_ip(self, session,
                      domain_uuid: str,
                      interface_name: str,
                      network_addr: str,
                      gateway: str,
                      remove: bool = False) -> APIResponse:
        """
        actually set domain's ip via qga, no db operations are involed.
        parameter remove controls wether its a remove operation
        note that domain must be running.
        """
        from src.guest.api import SlaveAPI, GuestAPI
        slave_api = SlaveAPI()
        guest_api = GuestAPI()
        
        try:
            slave_name = guest_api.get_domain_slave_name(domain_uuid).get_data()
            slave_address: str = slave_api.get_slave_address_by_name(slave_name).get_data()
            url = "http://"+ slave_address
            
            if remove == False:
                data = {
                        consts.P_DOMAIN_UUID: domain_uuid,
                        consts.P_NETWORK_ADDRESS: network_addr,
                        consts.P_GATEWAY: gateway,
                        consts.P_INTERFACE_NAME: interface_name
                    }
                response: requests.Response = requests.post(url + "/setStaticIP/", data)
                return APIResponse.deserialize_response(response.json())
            else:
                data = {
                        consts.P_DOMAIN_UUID: domain_uuid,
                        consts.P_INTERFACE_NAME: interface_name
                    }
                response: requests.Response = requests.post(url + "/removeStaticIP/", data)
                return APIResponse.deserialize_response(response.json())
            
        except Exception as e:
            return APIResponse.error(400, str(e))
        
        
    @enginefacade.transactional
    def list_networks(self, session):
        network_list: list[Network] = db.get_network_list(session)
        res = [network.to_dict() for network in network_list]
        return APIResponse.success(res)
    
    
    @enginefacade.transactional
    def list_interfaces(self, session):
        interface_list: list[Interface] = db.get_interface_list(session)
        res = [interface.to_dict() for interface in interface_list]
        return APIResponse.success(res)
    
    
    @enginefacade.transactional
    def list_domain_interfaces(self, session, domain_uuid)-> APIResponse:
        interfaces: list[Interface] = db.condition_select(session, Interface, values={"guest_uuid" : domain_uuid})
        res = [interface.to_dict() for interface in interfaces]
        return APIResponse.success(res)
    
    
    @enginefacade.transactional
    def network_detail(self, session, network_name: str):
        network: Network = db.get_network_by_name(session, network_name)
        if network is None:
            return APIResponse.error(code=400, msg=f'cannot find a network which name={network_name}')
        return APIResponse.success(network.to_dict())
    
    
    @enginefacade.transactional
    def interface_detail(self, session, interface_name: str):
        interface: Interface = db.get_interface_by_name(session, interface_name)
        if interface is None:
            return APIResponse.error(code=400, msg=f'cannot find a interface which name={interface_name}')
        return APIResponse.success(interface.to_dict())
    
    
    ####################
    # helper functions #
    ####################
    
def is_ip_in_network(ip_address_str: str, network_address_str: str) -> bool:
    """
    detarmine whether a ip address is within a network address

    Args:
        ip_address_str (str): eg: 20.0.0.11/24
        network_address_str (str): eg: 20.0.0.0/24

    """
    try:
        ip_network = ipaddress.IPv4Network(network_address_str, strict=False)
        ip = ipaddress.IPv4Interface(ip_address_str)

        return ip.ip in ip_network
    except ValueError as e:
        print(f"Error: {e}")
        return False
    
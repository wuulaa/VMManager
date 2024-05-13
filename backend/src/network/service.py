import requests
import ipaddress
import random
from src.utils.response import APIResponse
from src.utils.singleton import singleton
from src.domain_xml.device import interface as interface_xml
from src.common.network_manager import api as netapi
from src.network.db.models import Network, Interface, OVSPort
from src.network import db 
from src.utils.sqlalchemy import enginefacade
from src.utils.config import CONF
from src.utils import consts, generator
from faker import Faker
import inspect
from src.utils.jwt import check_user
from src.user.api import UserAPI
from src.user.db.models import User
from src.common.docker_manager.docker_manager import DockerManager

user_api = UserAPI()


@singleton
class NetworkServiceBase:
    """
    Base class for network service
    """
    @enginefacade.transactional
    def list_networks(self, session, user_name=None):
        if not check_user(user_name, User):
            return APIResponse.error(code=501, msg="wrong user")
        if user_name is None:
            network_list: list[Network] = db.get_network_list(session)
            res = [network.to_dict() for network in network_list]
            return APIResponse.success(res)
        else:
            user_uuid = user_api.get_user_uuid_by_name(user_name).get_data()
            network_list: list[Network] = db.get_user_network_list(session, user_uuid)
            res = [network.to_dict() for network in network_list]
            return APIResponse.success(res)
    
    
    @enginefacade.transactional
    def list_interfaces(self, session, user_name=None):
        if not check_user(user_name, User):
            return APIResponse.error(code=501, msg="wrong user")
        if user_name is None:
            interface_list: list[Interface] = db.get_interface_list(session)
            res = [interface.to_dict() for interface in interface_list]
            return APIResponse.success(res)
        else:
            user_uuid = user_api.get_user_uuid_by_name(user_name).get_data()
            interface_list: list[Interface] = db.get_user_interface_list(session, user_uuid)
            res = [interface.to_dict() for interface in interface_list]
            return APIResponse.success(res)
    
    
    @enginefacade.transactional
    def interface_exists(self, session, interface_name: str):
        interface = db.get_interface_by_name(session, interface_name)
        res = True
        if interface is None:
            res = False
        return APIResponse.success(data=res)
    
    
    @enginefacade.transactional
    def network_detail(self, session, network_name: str):
        if not check_user(network_name, Network):
            return APIResponse.error(code=501, msg="wrong user")
        network: Network = db.get_network_by_name(session, network_name)
        if network is None:
            return APIResponse.error(code=400, msg=f'cannot find a network which name={network_name}')
        return APIResponse.success(network.to_dict())
    
    
    @enginefacade.transactional
    def interface_detail(self, session, interface_name: str):
        if not check_user(interface_name, Interface):
            return APIResponse.error(code=501, msg="wrong user")
        interface: Interface = db.get_interface_by_name(session, interface_name)
        if interface is None:
            return APIResponse.error(code=400, msg=f'cannot find a interface which name={interface_name}')
        return APIResponse.success(interface.to_dict())
    
    
    @enginefacade.transactional
    def get_network_user_uuid(self, session, network_name):
        network:Network = db.get_network_by_name(session, name=network_name)
        if network is None:
            return APIResponse.error(code=400)
        return APIResponse.success(network.user_uuid)
    
    @enginefacade.transactional
    def get_interface_user_uuid(self, session, interface_name):
        interface:Interface = db.get_interface_by_name(session, name=interface_name)
        if interface is None:
             return APIResponse.error(code=400)
        return APIResponse.success(interface.user_uuid)


NetworkServiceBaseClass = NetworkServiceBase().__class__

@singleton
class NetworkService(NetworkServiceBaseClass):
    
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
            slaves = CONF['slaves']
            slave_count: int = 0
            for key in slaves.keys():
                slave_count = slave_count + 1
            bridge_prefix: str = CONF.get("network", "bridge_prefix")
            master_ip: str = CONF.get("master", "master").split(":")[0]
            
            master_bridge_name = bridge_prefix + "_master"
            slave_bridge_name = bridge_prefix + "_slave"
            
            # 1. create master bridge and nat network
            netapi.create_bridge(bridge_name=master_bridge_name)
            netapi.create_ovs_nat_network(network_address, master_bridge_name)
            netapi.init_iptables()
            
            # 2. create slave bridges and add gre ports
            # old version uses vxlan ports, but it conflicts with docker swarm
            # so we use gre instead
            i = 0
            for key, value in slaves.items():
                
                slave_address: str = value
                slave_ip: str = slave_address.split(":")[0]
                url = "http://"+ slave_address
                
                data = {
                    consts.P_BRIDGE_NAME: slave_bridge_name
                }
                response1 = requests.post(url + "/createBridge/", data)
                
                # master and slave cannot use the same remote ip
                data = {
                    consts.P_BRIDGE_NAME: slave_bridge_name,
                    # consts.P_PORT_NAME: f"vxlan_slave_{i}",
                    consts.P_PORT_NAME: f"gre_slave_{i}",
                    consts.P_REMOTE_IP: master_ip
                }
                response2 = APIResponse(requests.post(url + "/addGrePort/", data))
                i = i+1
                # TODO: single machine cannot hava same vlan ports, uncomment this for real cluster
                # netapi.add_vxlan_port_to_bridge(master_bridge_name, f"vxlan_master_{i}", slave_ip)
                netapi.add_gre_port_to_bridge(master_bridge_name, f"gre_master_{i}", slave_ip)
            
            # call ip link to set master up
            netapi.ip_link_set_up(bridge_prefix + "_master")
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
            slaves = CONF['slaves']
            slave_count: int = 0
            for key in slaves.keys():
                slave_count += 1
            bridge_prefix: str = CONF.get("network", "bridge_prefix")
            master_ip: str = CONF.get("master", "master").split(":")[0]
            
            master_bridge_name = bridge_prefix + "_master"
            slave_bridge_name = bridge_prefix + "_slave"
            
            # 1. delete master bridge and nat network
            netapi.delete_bridge(bridge_name=master_bridge_name)
            netapi.delete_ovs_nat_network(network_address)
            netapi.uninit_iptables()

            # 2. delete slave bridges
            for key, value in slaves.items():
                slave_address: str = value
                url = "http://"+ slave_address
                
                data = {
                    consts.P_BRIDGE_NAME: slave_bridge_name
                }
                response = requests.post(url + "/deleteBridge/", data)
                
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
        
        
    @enginefacade.transactional
    def create_network(self, session, name, ip_address):
        """
        create virtual network,
        this only needs to write db
        and add the gateway address to master bridge
        
        Args:
            name (str): name of the network
            ip_address (str): address of the network, eg: 1.2.3.4/24
        """
        try:
            user_uuid = user_api.get_current_user_uuid().get_data()
            if is_network_ip_used(ip_address):
                return APIResponse.error(code=400, msg="network ip has been used")
            network: Network = db.create_network(session, name=name, ip_address=ip_address, user_uuid=user_uuid)
            
            master_bridge_name = CONF.get("network", "bridge_prefix") + "_master"
            gateway = get_network_gateway_with_mask(ip_address)
            netapi.ip_link_add_addr(master_bridge_name, gateway)
            return APIResponse.success(network.uuid)
        
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    @enginefacade.transactional
    def reload_network(self, session):
        """
        reload virtual network after system reboot
        this only reads db 
        and add the gateway address to master bridge
        
        this function should be called during system booting
        """
        try:
            networks:list[Network] = db.get_ovs_network_list(session=session)
            master_bridge_name = CONF.get("network", "bridge_prefix") + "_master"
            for network in networks:
                gateway = get_network_gateway_with_mask(network.address)
                netapi.ip_link_add_addr(master_bridge_name, gateway)
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def delete_network(self, session, network_name):
        """
        delete virtual network,
        all virtual interfaces of the network would also be deleted

        Args:
            name (str): network name
        """
        try:
            if not check_user(network_name, Network):
                return APIResponse.error(code=501, msg="wrong user")
            network: Network = db.get_network_by_name(session, network_name)
            address = network.address
            if network is None:
                return APIResponse.error(code=400, msg=f'cannot find a network which name={network_name}')
            interfaces: list[Interface] = network.interfaces
            for interface in interfaces:
                self.delete_interface(session, interface.uuid)
            db.delete_network_by_name(session, network_name)
            
            master_bridge_name = CONF.get("network", "bridge_prefix") + "_master"
            gateway = get_network_gateway_with_mask(address)
            netapi.ip_link_del_addr(master_bridge_name, gateway)
            
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
    def interface_exists(self, session, interface_name: str):
        interface = db.get_interface_by_name(session, interface_name)
        res = True
        if interface is None:
            res = False
        return APIResponse.success(data=res)
    
    @enginefacade.transactional
    def create_interface(self, session,
                         interface_name: str,
                         network_name: str,
                         ip_address: str,
                         gateway: str, 
                         mac: str = None,
                         inerface_type: str = "direct"):
        """
        create virtual interface.
        if name or ip_address is none ,random name or address would be used
        this is a purely db function,
        real port is set during binding
        """
        
        # write interface db
        network: Network = db.get_network_by_name(session, network_name)
        if network is None:
            return APIResponse.error(400, f'cannot find a network which name={network_name}')
        
        
        try:
            interfaces: list[Interface] = db.get_interface_list()
            used_names: list[str] = [interface.name for interface in interfaces]
            ips: list[str] = [interface.ip_address for interface in interfaces]
            if interface_name is None:
                interface_name = generator.generage_unused_name(used_names)
            if ip_address is None:
                ip_address = generator.generate_unique_ip(network.address, ips)
            if mac is None:
                mac = generator.generate_random_mac()
            if gateway is None:
                gateway = get_network_gateway(ip_address)
            if gateway.find('/') != -1:
                gateway = gateway.split('/')[0]
                
            if not is_ip_in_network(ip_address, network.address):
                return APIResponse.error(400, f'interface address is not within network')
        
            if is_interface_ip_used(ip_address):
                return APIResponse.error(400, f'interface address has been used')
            
            user_uuid = user_api.get_current_user_uuid().get_data()
            interface: Interface = db.create_interface(session,
                                            name=interface_name,
                                            network_name=network_name,
                                            ip_address=ip_address,
                                            gateway=gateway,
                                            mac=mac,
                                            inerface_type=inerface_type,
                                            user_uuid=user_uuid)
            uuid = interface.uuid
            return APIResponse.success(data={"interface_uuid": uuid})
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    
        
    @enginefacade.transactional
    def delete_interface(self, session, interface_uuid: str=None, interface_name: str = None):
        if not check_user(interface_name, Interface):
            return APIResponse.error(code=501, msg="wrong user")
        try:
            if interface_uuid:
                interface: Interface = db.get_interface_by_uuid(session, interface_uuid)
            elif interface_name:
                interface: Interface = db.get_interface_by_name(session, interface_name)
                
        
            if interface is None:
                return APIResponse.error(code=400, msg=f'cannot find a interface which name={interface_name}, uuid={interface_uuid}')
            
            interface_uuid = interface.uuid
            if interface.guest_uuid is not None:
                return APIResponse.error(code=400, msg=f'interface is used by domain whose uuid={interface_uuid}')
            
            # 1.if in bound,  unbound the interace
            if interface.status != "unbound":
                self.unbind_interface_port(session, interface_uuid)
            
            # 2. delete in db
            db.delete_interface_by_uuid(session, interface_uuid)
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
        
        
    @enginefacade.transactional
    def clone_interface(self, session, interface_uuid: str, interface_name: str = None, new_name = None, new_ip = None):
        """
        clone a interface, if new_ip is None, a random available ip within the network would be selected.
        this is also a purly db function

        """
        if not check_user(interface_name, Interface):
            return APIResponse.error(code=501, msg="wrong user")
        if interface_uuid is not None:
            interface: Interface = db.get_interface_by_uuid(interface_uuid)
        else:
            interface: Interface = db.get_interface_by_name(interface_name)
            
        if interface is None:
            return APIResponse.error(code=400, msg=f'cannot find a interface which name={interface_name}, uuid = {interface_uuid}')
        network: Network = db.get_network_by_uuid(interface.network_uuid)
        interfaces: list[Interface] = db.get_interface_list()
        used_names: list[str] = [interface.name for interface in interfaces]
        ips: list[str] = [interface.ip_address for interface in interfaces]
        
        if new_name is None:
            new_name = generator.generage_unused_name(used_names)
            
        if new_ip is None:
            new_ip = generator.generate_unique_ip(network.address, ips)
        else:
            if not is_ip_in_network(new_ip, network.address):
                return APIResponse.error(code=400, msg="new ip is not within network scope")
            
        mac = generator.generate_random_mac()
         
        return self.create_interface(session, interface_name=new_name, network_name=network.name,
                              ip_address=new_ip, gateway=interface.gateway, mac=mac)
    
    
    
    @enginefacade.transactional
    def modify_interface(self, session, interface_uuid: str = None, interface_name: str = None, ip_addr: str = None, gateway:str =None):
        """
        modify interface, currently supports ip and gateway only,
        make sure to pass them both
        """
        from src.guest.api import GuestAPI
        guest_api = GuestAPI()
        
        if not check_user(interface_name, Interface):
            return APIResponse.error(code=501, msg="wrong user")
        try:
            if interface_uuid:
                interface: Interface = db.get_interface_by_uuid(session, interface_uuid)
            elif interface_name:
                interface: Interface = db.get_interface_by_name(session, interface_name)
                
            if interface is None:
                return APIResponse.error(code=400, msg=f'cannot find a interface which name={interface_name}, uuid = {interface_uuid}')
            
            remove_domain_ip = False
            if gateway is None and ip_addr is None:
                remove_domain_ip = True
            else:
                if gateway is None:
                    gateway = interface.gateway
                if ip_addr is None:
                    ip_addr = interface.ip_address
            
            network: Network = db.get_network_by_uuid(interface.network_uuid)
            if not is_ip_in_network(ip_addr, network.address):
                return APIResponse.error(code=400, msg="new ip is not within network scope")
                
            # 1. update in db
            db.update_interface_ip(session, interface.uuid, ip_addr)
            db.update_interface_gateway(session, interface.uuid, gateway)
            # 2. check if is used in domain
            if interface.guest_uuid is not None:
                    
                domain_status = guest_api.get_domain_status(interface.guest_uuid).get_data()
                if domain_status == "running":
                    # if domain is running, directly change the ip/gateway
                    self.set_domain_ip(session, interface.guest_uuid,
                                    interface.name, ip_addr, gateway, remove_domain_ip)
                else:
                    # else set interface as modified, ip change would apply after starting domain
                    # db.update_interface_modified(session, interface.uuid, True)
                    pass
                    
            return APIResponse.success()
        
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
            slave_uuid: str = slave_api.get_slave_by_name(slave_name).get_data().uuid
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
            db.update_interface_status(session, interface_uuid, "unbound")
            db.update_interface_slave_uuid(session, interface_uuid, None)
            db.update_interface_xml(session, interface_uuid, None)
            db.update_interface_veth_name(session, interface_uuid, None)
            
            return APIResponse.success()
        except Exception as e:
            raise e
    
    
    @enginefacade.transactional
    def update_domain_veth_name(self, session, domain_uuid):
        from src.guest.api import SlaveAPI, GuestAPI
        slave_api = SlaveAPI()
        guest_api = GuestAPI()
        
        try:
            slave_name: str = guest_api.get_domain_slave_name(domain_uuid).get_data()
            slave_address: str = slave_api.get_slave_address_by_name(slave_name).get_data()
            url = "http://"+ slave_address
            data = {
                    consts.P_DOMAIN_UUID: domain_uuid
                }
            response: requests.Response = requests.post(url + "/getInterfaceAddresses/", data)
            apires: APIResponse = APIResponse().deserialize_response(content=response.json())
            res_dict: dict = apires.get_data()
            
            interfaces: list[Interface] = db.condition_select(session, Interface, values={"guest_uuid" : domain_uuid})
            
            for interface in interfaces:
                mac = interface.mac
                for key, info in res_dict.items():
                    if "hwaddr" in info and info.get('hwaddr') == mac:
                        db.update_interface_veth_name(session, interface.uuid, key)
            
            return APIResponse.success()
                        
        except Exception as e:
            raise e
        
        
    @enginefacade.transactional
    def init_set_domain_static_ip(self, session, domain_uuid):
        from src.guest.api import SlaveAPI, GuestAPI
        slave_api = SlaveAPI()
        guest_api = GuestAPI()
        try:
            slave_name: str = guest_api.get_domain_slave_name(domain_uuid).get_data()
            slave_address: str = slave_api.get_slave_address_by_name(slave_name).get_data()
            url = "http://"+ slave_address
            
            self.update_domain_veth_name(session, domain_uuid)
            
            
            interfaces: list[Interface] = db.condition_select(session, Interface, values={"guest_uuid" : domain_uuid})
            # if len(interfaces) == 0:
            #     return APIResponse.success()
            
            veth_names = [interface.veth_name for interface in interfaces]
            ips = [interface.ip_address for interface in interfaces]
            gateways = [interface.gateway for interface in interfaces]
            
            data = {
                    consts.P_DOMAIN_UUID: domain_uuid,
                    consts.P_IP_ADDRESSES: ",".join(ips),
                    consts.P_GATEWAYS: ",".join(gateways),
                    consts.P_INTERFACE_NAMES: ",".join(veth_names)
                    }
            response: requests.Response = requests.post(url + "/initSetStaticIP/", data)
            apires: APIResponse = APIResponse().deserialize_response(content=response.json())
            if apires.get_code() != 0:
                return apires
            return APIResponse.success()
        except Exception as e:
            return APIResponse.error(code=400, msg=str(e))
    
    
    @enginefacade.transactional
    def get_interface_xml(self, session, interface_name: str):
        interface: Interface = db.get_interface_by_name(session, interface_name)
        if interface is None:
            return APIResponse.error(400, f"cannot find interface with name = {interface_name}")
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
            slave_name = guest_api.get_domain_slave_name(domain_uuid).get_data()

            
            self.bind_interface_to_port(session, interface.uuid, slave_name)
            db.update_interface_guest_uuid(session, interface.uuid, domain_uuid)
            db.update_interface_status(session, interface.uuid, "bound_in_use")
            
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

    
    
    @enginefacade.transactional
    def set_domain_ip(self, session,
                      domain_uuid: str,
                      interface_name: str,
                      ip_addr: str,
                      gateway: str,
                      remove: bool = False) -> APIResponse:
        """
        actually set domain's ip via qga, no db operations are involed.
        parameter 'remove' controls wether its a remove operation
        note that domain must be running.
        """
        from src.guest.api import SlaveAPI, GuestAPI
        slave_api = SlaveAPI()
        guest_api = GuestAPI()
        
        try:
            slave_name = guest_api.get_domain_slave_name(domain_uuid).get_data()
            slave_address: str = slave_api.get_slave_address_by_name(slave_name).get_data()
            url = "http://"+ slave_address
            
            interface: Interface = db.get_interface_by_name(session, interface_name)
            veth_name = interface.veth_name
            
            if remove == False:
                data = {
                        consts.P_DOMAIN_UUID: domain_uuid,
                        consts.P_IP_ADDRESS: ip_addr,
                        consts.P_GATEWAY: gateway,
                        consts.P_INTERFACE_NAME: veth_name
                    }
                response: requests.Response = requests.post(url + "/setStaticIP/", data)
                return APIResponse().deserialize_response(response.json())
            else:
                data = {
                        consts.P_DOMAIN_UUID: domain_uuid,
                        consts.P_INTERFACE_NAME: veth_name
                    }
                response: requests.Response = requests.post(url + "/removeStaticIP/", data)
                return APIResponse().deserialize_response(response.json())
            
        except Exception as e:
            return APIResponse.error(400, str(e))
        
    
    @enginefacade.transactional
    def list_domain_interfaces(self, session, domain_uuid)-> APIResponse:
        interfaces: list[Interface] = db.condition_select(session, Interface, values={"guest_uuid" : domain_uuid})
        res = [interface.to_dict() for interface in interfaces]
        return APIResponse.success(res)
    
    
    @enginefacade.transactional
    def get_domain_interface_names(self, session, domain_uuid: str):
        res: list[Interface] = db.get_domain_interfaces(session, domain_uuid)
        names = [interface.name  for interface in res]
        return APIResponse.success(names)
    
    
    
class DockerNetworkService(NetworkServiceBaseClass):
    
    @enginefacade.transactional
    def create_docker_top_network(self, session,
                                  network_address: str=None):
        '''
        This is an initial function which creates top level network for docker.
        We use docker swarm to setup the vxlan network.
        The master node would be swarm master and call swarm init.
        Slave nodes would abso be swarm masters and call swarm join.
        If slave is worker, network list would not get overlay networks, 
        so they are also treated as masters.
        Docker itself handles NAT and bridge creation.
        
        '''
        try:
            slaves = CONF['slaves']
            master_ip: str = CONF.get("master", "master").split(":")[0]
            # swarm_name = CONF.get("network", "bridge_prefix") + "_swarm"
            res_flag = True
            docker_manager = DockerManager()
            address_lst = []
            address_lst.append(network_address)
            # 1. swarm init
            response = docker_manager.init_swarm(default_addr_pool=address_lst)
            swarm_token = docker_manager.get_swarm_manager_token().get_data()
            if not response.is_success():
                res_flag = False
            
            # 2. join swarm
            for key, value in slaves.items():
                
                slave_address: str = value
                url = "http://"+ slave_address
                
                data = {
                    consts.P_SWARM_MANAGER_TOKEN: swarm_token,
                    consts.P_REMOTE_ADDRS: master_ip + ":2377"
                    
                }
                response = APIResponse().deserialize_response(requests.post(url + "/joinSwarm/", data).json())
                if not response.is_success():
                    res_flag = False
            
            if res_flag:
                return APIResponse.success()
            else:
                docker_manager.leave_swarm(force=True)
                return APIResponse.error(code=400, msg="swarm init/join failed")
            
            
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def delete_docker_top_network(self, session):
        try:
            slaves = CONF['slaves']
            res_flag = True
            
            # 1. leave swarm
            for key, value in slaves.items():
                slave_address: str = value
                url = "http://"+ slave_address
                
                data = {
                    consts.P_FORCE: True
                }
                response = APIResponse().deserialize_response(requests.post(url + "/leaveSwarm/", data).json())
                if not response.is_success():
                    res_flag = False
            
            
            # 2. swarm dismiss
            docker_manager = DockerManager()
            response = docker_manager.leave_swarm(True)
            if not response.is_success():
                res_flag = False
            
            
            if res_flag:
                return APIResponse.success()
            else:
                return APIResponse.error(code=400, msg="swarm dismiss/leave failed")
            
            
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def create_docker_network(self, session, name:str, ip_address:str):
        """
        Create virtual docker network,
        this writes db and create swarm subnet
        
        Args:
            name (str): name of the network
            ip_address (str): address of the network, eg: 1.2.3.4/24
        """
        try:
            user_uuid = user_api.get_current_user_uuid().get_data()
            if is_network_ip_used(ip_address):
                return APIResponse.error(code=400, msg="network ip has been used")
            
            gateway = get_network_gateway(ip_address)
            
            # 1. create swarm subnet
            docker_manager = DockerManager()
            resp = docker_manager.crate_network(name=name, subnet=ip_address, gateway=gateway)
            #TODO: make use of this?
            network_id = resp.get_data()
                        
            # 2. write db
            network: Network = db.create_network(session, name=name, ip_address=ip_address,
                                                 user_uuid=user_uuid, network_type="docker_swarm")
            return APIResponse.success(network.uuid)
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def delete_docker_network(self, session, network_name:str):
        try:
            if not check_user(network_name, Network):
                return APIResponse.error(code=501, msg="wrong user")
            network: Network = db.get_network_by_name(session, network_name)
            if network is None:
                return APIResponse.error(code=400, msg=f'cannot find a network which name={network_name}')
            
            # 1. delete swarm subnet
            docker_manager = DockerManager()
            docker_manager.delete_network(name=network_name)
            
            # 2. write db
            interfaces: list[Interface] = network.interfaces
            for interface in interfaces:
                self.delete_docker_interface(session, interface.uuid)
            db.delete_network_by_name(session, network_name)
                 
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def create_docker_interface(self, session, 
                                interface_name: str,
                                network_name: str,
                                ip_address: str,
                                gateway: str, 
                                inerface_type: str = "docker_overlay"):
        # write interface db
        network: Network = db.get_network_by_name(session, network_name)
        if network is None:
            return APIResponse.error(400, f'cannot find a network which name={network_name}')
        
        
        try:
            interfaces: list[Interface] = db.get_interface_list()
            used_names: list[str] = [interface.name for interface in interfaces]
            ips: list[str] = [interface.ip_address for interface in interfaces]
            if interface_name is None:
                interface_name = generator.generage_unused_name(used_names)
            if ip_address is None:
                ip_address = generator.generate_unique_ip(network.address, ips)
            if gateway is None:
                gateway = get_network_gateway(ip_address)
            if gateway.find('/') != -1:
                gateway = gateway.split('/')[0]
                
            if not is_ip_in_network(ip_address, network.address):
                return APIResponse.error(400, f'interface address is not within network')
        
            if is_interface_ip_used(ip_address):
                return APIResponse.error(400, f'interface address has been used')
            
            user_uuid = user_api.get_current_user_uuid().get_data()
            interface: Interface = db.create_interface(session,
                                            name=interface_name,
                                            network_name=network_name,
                                            ip_address=ip_address,
                                            gateway=gateway,
                                            mac="Determined by docker",
                                            inerface_type=inerface_type,
                                            user_uuid=user_uuid,
                                            network_type="docker_swarm")
            uuid = interface.uuid
            return APIResponse.success(data={"interface_uuid": uuid})
        except Exception as e:
            return APIResponse.error(400, str(e))
    
        
    @enginefacade.transactional
    def delete_docker_interface(self, session, 
                                interface_uuid: str=None, 
                                interface_name: str = None):
        if not check_user(interface_name, Interface):
            return APIResponse.error(code=501, msg="wrong user")
        try:
            interface = None
            if interface_uuid:
                interface: Interface = db.get_interface_by_uuid(session, interface_uuid)
            elif interface_name:
                interface: Interface = db.get_interface_by_name(session, interface_name)
                
        
            if interface is None:
                return APIResponse.error(code=400, msg=f'cannot find a interface which name={interface_name}, uuid={interface_uuid}')
            
            interface_uuid = interface.uuid
            if interface.guest_uuid is not None:
                return APIResponse.error(code=400, msg=f'interface is used by container whose uuid={interface_uuid}')
            
            # 1.if in bound,  unbound the interace
            # TODO: disconnect
            
            # 2. delete in db
            db.delete_interface_by_uuid(session, interface_uuid)
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def add_interface_to_container(self, session,
                                   interface_name:str,
                                   container_uuid:str):
        """
        This in fact uses 'docker network connect' which connects container to network.
        """
        from src.docker.api import DockerAPI
        from src.guest.api import SlaveAPI
        docker_api = DockerAPI()
        slave_api = SlaveAPI()
        try:
            interface: Interface = db.get_interface_by_name(session, interface_name)
            if interface.status == "bound_in_use" or interface.guest_uuid is not None:
                return APIResponse.error(401, "interface already in use")
            
            slave_name = docker_api.get_slave_name(container_uuid).get_data()
            slave_address: str = slave_api.get_slave_address_by_name(slave_name).get_data()
            slave_uuid: str = slave_api.get_slave_by_name(slave_name).get_data().uuid
            url = "http://"+ slave_address
            
            container_id = docker_api.get_container_id(container_uuid).get_data()
            network_name = db.get_network_by_uuid(session, interface.network_uuid).name
            ip_address = interface.ip_address
            
            
            # 1. connect container to network
            data = {
                consts.P_CONTAINER_ID: container_id,
                consts.P_NETWORK_NAME: network_name,
                consts.P_IP_ADDRESS: ip_address
            }
            response: requests.Response = requests.post(url + "/connectNetwork/", data)
            apires: APIResponse = APIResponse().deserialize_response(content=response.json())
            if not apires.is_success():
                return apires
            
            # 2. write db    
            db.update_interface_guest_uuid(session, interface.uuid, container_uuid)
            db.update_interface_status(session, interface.uuid, "bound_in_use")
            db.update_interface_slave_uuid(session, interface.uuid, slave_uuid)
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
        
        
    
    @enginefacade.transactional
    def remove_interface_from_container(self, session,
                                        interface_name:str):
        """
        Call 'docker network disconnect'
        """
        from src.docker.api import DockerAPI
        from src.guest.api import SlaveAPI
        docker_api = DockerAPI()
        slave_api = SlaveAPI()
        try:
            interface: Interface = db.get_interface_by_name(session, interface_name)
            if interface.status != "bound_in_use" or interface.guest_uuid is None:
                return APIResponse.error(401, "interface not used by container")
            
            container_uuid = interface.guest_uuid
            slave_name = docker_api.get_slave_name(container_uuid).get_data()
            slave_address: str = slave_api.get_slave_address_by_name(slave_name).get_data()
            url = "http://"+ slave_address
            container_id = docker_api.get_container_id(container_uuid).get_data()
            network_name = db.get_network_by_uuid(session, interface.network_uuid).name
            
            
            # 1. disconnect container from network
            data = {
                consts.P_CONTAINER_ID: container_id,
                consts.P_NETWORK_NAME: network_name
            }
            response: requests.Response = requests.post(url + "/disconnectNetwork/", data)
            apires: APIResponse = APIResponse().deserialize_response(content=response.json())
            if not apires.is_success():
                return apires
            
            # 2. write db    
            db.update_interface_guest_uuid(session, interface.uuid, None)
            db.update_interface_status(session, interface.uuid, "unbound")
            db.update_interface_slave_uuid(session, interface.uuid, None)
            
            return APIResponse.success()
        
        except Exception as e:
            return APIResponse.error(400, str(e))
    
    
    @enginefacade.transactional
    def list_container_interfaces(self, session, container_uuid:str):
        interfaces: list[Interface] = db.condition_select(session, Interface, values={"guest_uuid" : container_uuid})
        res = [interface.to_dict() for interface in interfaces]
        return APIResponse.success(res)
    
    
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
    
    
def is_interface_ip_used(ip_address: str) -> bool:
    """
    check db and see if ip has been used by interface
    """
    interfaces: list[Interface] = db.get_interface_list()
    ips: list[str] = [interface.ip_address for interface in interfaces]
    if ip_address in ips:
        return True
    else:
        return False
    

def is_network_ip_used(network_address: str) -> bool:
    """
    check db and see if network ip has been used
    """
    networks: list[Network] = db.get_network_list()
    ips: list[str] = [network.address for network in networks]
    if network_address in ips:
        return True
    else:
        return False
            

def get_network_gateway(ip_address_str: str) -> str:
    try:
        ip_interface = ipaddress.IPv4Interface(ip_address_str)
        network = ip_interface.network

        # 获取网络的第一个地址作为网关
        gateway_ip = str(network.network_address + 1)
        return gateway_ip

    except ValueError as e:
        print(f"Error: {e}")
        return None

def get_network_gateway_with_mask(ip_address_str: str) -> str:
    try:
        ip_interface = ipaddress.IPv4Interface(ip_address_str)
        network = ip_interface.network

        # 获取网络的第一个地址作为网关
        gateway_ip = str(network.network_address + 1)
        subnet_mask = '/' + str(network.prefixlen)

        return gateway_ip + subnet_mask

    except ValueError as e:
        print(f"Error: {e}")
        return None


# def check_user_decorator(identifier, model):
#     """
#     decorator for checking user uuid
#     for example, check whether current user has the domain/interface/volume
#     """
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             from src.user.api import UserAPI
#             user_api = UserAPI()
#             network_service = NetworkService()
            
#             # 使用inspect模块的signature函数获取函数的参数签名
#             signature = inspect.signature(func)
#             # 获取参数名列表
#             parameter_names = list(signature.parameters.keys())
#             parameters_dict = {param_name: arg for param_name, arg in zip(parameter_names, args)}
#             parameters_dict.update(kwargs)
            
#             identifier_value = None
#             for key, value in parameters_dict.items():
#                 if key == identifier:
#                     identifier_value = value
            
#             if model == Network:
#                 network_user_uuid = network_service.get_network_user_uuid(network_name=identifier_value).get_data()
#                 current_user_uuid = user_api.get_current_user_uuid().get_data()
#                 if network_user_uuid != current_user_uuid:
#                     return APIResponse.error(code=405, msg="wrong user")
                
            
#             # 调用原始函数并返回结果
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator


        
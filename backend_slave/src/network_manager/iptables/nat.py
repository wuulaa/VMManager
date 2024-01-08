from src.network_manager.iptables.iptables import *
from src.utils.response import APIResponse 

def append_drop_to_forward():
    append_rule_cmd(FILTER, FORWARD, f"-j DROP")


def create_ovs_nat_network(network_addr:str, bridge_name: str):
    '''
    create nat network for a ovs bridge,
    ports on the bridge could access internet via this
    network_addr example: 1.2.3.4/24
    '''
    chain_prefix = network_addr.replace("/","_").replace(".", "_")
    nat_chain_name = "NAT" + chain_prefix
    filter_chain_name = "FORWARD" + chain_prefix
    create_chain_cmd(NAT, nat_chain_name)
    
    results = []
    results.append(create_chain_cmd(FILTER, filter_chain_name))
    
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} -d 224.0.0.0/24 -j RETURN"))
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} -d 255.255.255.255/32 -j RETURN"))
    # results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} ! -d {network_addr} -p tcp -j MASQUERADE --to-ports 1024-65535"))
    # results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} ! -d {network_addr} -p udp -j MASQUERADE --to-ports 1024-65535"))
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} ! -d {network_addr} -j MASQUERADE"))
    
    # results.append(append_rule_cmd(FILTER, filter_chain_name, f"-d {network_addr} -o {bridge_name} -j ACCEPT"))
    # results.append(append_rule_cmd(FILTER, filter_chain_name, f"-s {network_addr} -i {bridge_name} -j ACCEPT"))
    results.append(append_rule_cmd(FILTER, filter_chain_name, f"! -s {network_addr} -d {network_addr} -o {bridge_name} -j ACCEPT"))
    results.append(append_rule_cmd(FILTER, filter_chain_name, f"-s {network_addr} ! -d {network_addr} -i {bridge_name} -j ACCEPT"))
    # results.append(append_rule_cmd(FILTER, filter_chain_name, f"-i {bridge_name} -o {bridge_name} -j ACCEPT"))
    
    
    results.append(insert_chain_reference_cmd(NAT, POSTROUTING, nat_chain_name))
    results.append(insert_chain_reference_cmd(FILTER, FORWARD, filter_chain_name))
    
    results.append(create_route_chain(network_addr))
    
    
    for res in results:
        if res.get_code() != 0:
            return(APIResponse.error(code=400))
    
    return APIResponse.success()



def delete_ovs_nat_network(network_addr:str):
    '''
    delete a ovs nat network
    '''
    chain_prefix = network_addr.replace("/","_").replace(".", "_")
    nat_chain_name = "NAT" + chain_prefix
    filter_chain_name = "FORWARD" + chain_prefix
    
    res1 = delete_chain_cmd(NAT, POSTROUTING, nat_chain_name)
    res2 = delete_chain_cmd(FILTER, FORWARD, filter_chain_name)
    if res1.get_code() == 0 and res2.get_code() == 0:
        return APIResponse.success()
    
    return APIResponse.error(code=400)


def create_route_chain(network_addr:str):
    chain_name = "ROUTE" + network_addr.replace("/","_").replace(".", "_")
    parent_chain_name = "FORWARD" + network_addr.replace("/","_").replace(".", "_")
    create_chain_cmd(FILTER, chain_name)
    append_chain_reference_cmd(FILTER, parent_chain_name, chain_name)
    return APIResponse.success()


def create_route_networks(network_addrA:str, network_addrB:str, parent_addr:str):
    '''
    make two networks being connected
    '''
    parent_chain_name = "ROUTE" + parent_addr.replace("/","_").replace(".", "_")
    
    res1 = append_rule_cmd(FILTER, parent_chain_name, f"-s {network_addrA} -d {network_addrB} -j ACCEPT")
    res2 = append_rule_cmd(FILTER, parent_chain_name, f"-s {network_addrB} -d {network_addrA} -j ACCEPT")
    if res1.get_code() == 0 and res2.get_code() == 0:
        return APIResponse.success()
    
    return APIResponse.error(code=400)
    

def delete_route_networks(network_addrA:str, network_addrB:str, parent_addr:str):
    '''
    make two routed networks no longer connected
    '''
    parent_chain_name = "ROUTE" + parent_addr.replace("/","_").replace(".", "_")
    
    res1 = delete_rule_cmd(FILTER, parent_chain_name, f"-s {network_addrA} -d {network_addrB} -j ACCEPT")
    res2 = delete_rule_cmd(FILTER, parent_chain_name, f"-s {network_addrB} -d {network_addrA} -j ACCEPT")
    if res1.get_code() == 0 and res2.get_code() == 0:
        return APIResponse.success()
    
    return APIResponse.error(code=400)

# create_ovs_nat_network("20.0.0.0/8", "york")
# append_drop_to_forward()
# delete_ovs_nat_network("20.0.0.0/8")
# create_route_networks("20.0.0.0/24", "20.0.1.0/24", "20.0.0.0/8")
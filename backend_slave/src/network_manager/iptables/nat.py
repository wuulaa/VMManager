from src.network_manager.iptables.iptables import *
from src.utils.response import APIResponse 


def create_ovs_nat_network(network_addr:str, bridge_name: str):
    '''
    create nat network for a ovs bridge,
    ports on the bridge could access internet via this
    network_addr example: 1.2.3.4/24
    '''
    chain_prefix = network_addr.replace("/","_").replace(".", "_")
    nat_chain_name = "NAT" + chain_prefix
    filter_chain_name = "FILTER" + chain_prefix
    create_chain_cmd(NAT, nat_chain_name)
    
    results = []
    results.append(create_chain_cmd(FILTER, filter_chain_name))
    
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} -d 224.0.0.0/24 -j RETURN"))
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} -d 255.255.255.255/32 -j RETURN"))
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} ! -d {network_addr} -p tcp -j MASQUERADE --to-ports 1024-65535"))
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} ! -d {network_addr} -p udp -j MASQUERADE --to-ports 1024-65535"))
    results.append(append_rule_cmd(NAT, nat_chain_name, f"-s {network_addr} ! -d {network_addr} -j MASQUERADE"))
    
    results.append(append_rule_cmd(FILTER, filter_chain_name, f"-d {network_addr} -o {bridge_name} -j ACCEPT"))
    results.append(append_rule_cmd(FILTER, filter_chain_name, f"-s {network_addr} -i {bridge_name} -j ACCEPT"))
    results.append(append_rule_cmd(FILTER, filter_chain_name, f"-i {bridge_name} -o {bridge_name} -j ACCEPT"))
    
    results.append(insert_chain_reference_cmd(NAT, POSTROUTING, nat_chain_name))
    results.append(insert_chain_reference_cmd(FILTER, FORWARD, filter_chain_name))
    
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
    filter_chain_name = "FILTER" + chain_prefix
    
    res1 = delete_chain_cmd(NAT, POSTROUTING, nat_chain_name)
    res2 = delete_chain_cmd(FILTER, FORWARD, filter_chain_name)
    if res1.get_code() == 0 and res2.get_code() == 0:
        return APIResponse.success()
    
    return APIResponse.error(code=400)
    


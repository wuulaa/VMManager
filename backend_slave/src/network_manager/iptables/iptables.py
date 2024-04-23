# import iptc
import subprocess
from src.utils.response import APIResponse

INPUT = "INPUT"
OUTPUT = "OUTPUT"
PREROUTING = "PREROUTING"
POSTROUTING = "POSTROUTING"
FORWARD = "FORWARD"

FILTER = "filter"
MANGLE = "mangle"
RAW = "raw"
NAT = "nat"

MASQUERADE = "MASQUERADE"


# def dump_table(table_name: str):
#     try:
#         table_info = iptc.iptc.easy.dump_table(table_name)
#         return APIResponse.success(table_info)
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))
    
    
# def dump_chain(table_name: str, chain_name:str):
#     try:
#         table_info = iptc.iptc.easy.dump_chain(table_name, chain_name)
#         return APIResponse.success(table_info)
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


# def create_chain(table_name: str, chain_name: str):
#     try:
#         table = iptc.Table(table_name)
#         if table.is_chain(chain_name):
#             return APIResponse.error(400, "Error: chain already exists.")
#         table.create_chain(chain_name)
#         return APIResponse.success()
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


# def delete_chain(table_name: str, chain_name: str):
#     try:
#         table = iptc.Table(table_name)
#         if table.builtin_chain(chain_name):
#             return APIResponse.error(400, "Error: cannot delete builtin chain.")
#         if not table.is_chain(chain_name):
#             return APIResponse.error(400, "Error: chain does not exist.")
        
#         table.delete_chain(chain_name)
#         return APIResponse.success()
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


# def rename_chain(table_name: str, chain_name: str):
#     try:
#         table = iptc.Table(table_name)
#         if table.builtin_chain(chain_name):
#             return APIResponse.error(400, "Error: cannot rename builtin chain.")
#         if not table.is_chain(chain_name):
#             return APIResponse.error(400, "Error: chain does not exist.")
        
#         table.rename_chain(chain_name)
#         return APIResponse.success()
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


# def dump_chain(table_name: str, chain_name: str):
#     try:
#         chain_info = iptc.iptc.easy.dump_chain(table_name, chain_name)
#         return APIResponse.success(chain_info)
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


# def create_rule(src=None, dst=None,
#                 in_interface=None, out_interface=None,
#                 jump=None, to_ports=None, 
#                 protocol=None,
#                 sport=None, dport=None,
#                 state=None):
#     rule = iptc.Rule()
    
#     if src is not None:
#         rule.src = src
#     if dst is not None:
#         rule.dst = dst
#     if in_interface is not None:
#         rule.in_interface = in_interface
#     if out_interface is not None:
#         rule.out_interface = out_interface
    
#     target = iptc.Target(rule, jump)
    
#     if to_ports is not None:
#         target.to_ports = to_ports
#     rule.target = target
    
#     if protocol is not None:
#         rule.protocol = protocol
#         match = iptc.Match(rule, protocol)
        
#         if sport is not None:
#             match.sport = sport
#         if dport is not None:
#             match.dport = dport
#         if state is not None:
#             match.state = state
        
#         rule.add_match(match)

#     return rule


# def create_rule_from_dict(rule_dict: dict):
#     rule: iptc.Rule = iptc.iptc.easy.encode_iptc_rule(rule_dict)
#     return rule
    

# def append_rule(table_name: str, chain_name: str, rule_dict: dict):
#     try:
#         table = iptc.Table(table_name)
#         if not table.is_chain(chain_name):
#             return APIResponse.error(400, "Error: chain does not exist.")
#         chain = iptc.Chain(table, chain_name)
#         rule = create_rule_from_dict(rule_dict)
#         chain.append_rule(rule)
#         return APIResponse.success()
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


# def insert_rule(table_name: str, chain_name: str, rule_dict: dict):
#     try:
#         table = iptc.Table(table_name)
#         if not table.is_chain(chain_name):
#             return APIResponse.error(400, "Error: chain does not exist.")
#         chain = iptc.Chain(table, chain_name)
#         rule = create_rule_from_dict(rule_dict)
#         chain.insert_rule(rule)
#         return APIResponse.success()
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


# def delete_rule(table_name: str, chain_name: str, rule_dict: dict):
#     try:
#         iptc.iptc.easy.delete_rule(table_name, chain_name, rule_dict)
#         return APIResponse.success()
#     except iptc.IPTCError as err:
#         return APIResponse.error(400, str(err))


######## cmd #########


def append_rule_cmd(table_name: str, chain_name: str, rule):
    '''
    append a rule to a chain
    '''
    cmd = f"iptables -t {table_name} -A {chain_name} {rule}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)
    

def insert_rule_cmd(table_name: str, chain_name: str, rule):
    '''
    insert a rule to the beginning of a chain
    '''
    cmd = f"iptables -t {table_name} -I {chain_name} {rule}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)


def delete_rule_cmd(table_name: str, chain_name: str, rule):
    '''
    delete a rule from chain
    '''
    cmd = f"iptables -t {table_name} -D {chain_name} {rule}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)


def create_chain_cmd(table_name: str, chain_name: str):
    '''
    create a chain
    '''
    cmd = f"iptables -t {table_name} -N {chain_name}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)


def insert_chain_reference_cmd(table_name: str, parent_chain_name: str, reffered_chain_name: str):
    '''
    insert a chain reference to another chain
    '''
    cmd = f"iptables -t {table_name} -I {parent_chain_name} -j {reffered_chain_name}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)


def append_chain_reference_cmd(table_name: str, parent_chain_name: str, reffered_chain_name: str):
    '''
    append a chain reference to another chain
    '''
    cmd = f"iptables -t {table_name} -A {parent_chain_name} -j {reffered_chain_name}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)


def delete_chain_cmd(table_name: str, parent_chain_name: str, chain_name: str):
    '''
    delete a chain from table,
    reference is also deleted
    '''
    cmd1 = f"iptables -t {table_name} -F {chain_name}"
    res1 = subprocess.call(cmd1, shell=True)
    cmd2 = f"iptables -t {table_name} -D {parent_chain_name} -j {chain_name}"
    res2 = subprocess.call(cmd2, shell=True)
    cmd3 = f"iptables -t {table_name} -X {chain_name}"
    res3 = subprocess.call(cmd3, shell=True)
    if res1 == 0 and res2 == 0 and res3 == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)


def dump_table_cmd(table_name: str):
    '''
    dump table content
    '''
    cmd = f"iptables -t {table_name} -nvL"
    res = subprocess.run(cmd, shell=True,capture_output=True)
    if res.returncode == 0:
        return APIResponse.success(data=res.stdout)
    return APIResponse.error(code=400, msg=res.stderr)


def dump_chain_cmd(table_name: str, chain_name: str):
    '''
    dump chain content
    '''
    cmd = f"iptables -t {table_name} -nvL {chain_name}"
    res = subprocess.run(cmd, shell=True, capture_output=True)
    if res.returncode == 0:
        return APIResponse.success(data=res.stdout.decode("utf-8"))
    return APIResponse.error(code=400, msg=res.stderr.decode("utf-8"))


def iptables_save_cmd(file_path: str):
    '''
    save iptables rules to a file,
    save to system if no file name is provided
    '''
    if file_path is None:
        cmd = f"iptables-save"
    else:
        cmd = f"iptables-save > {file_path}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)


def restore_iptables_from_file(file_path: str):
    '''
    restore iptables rules from file
    '''
    cmd = f"iptables-restore < {file_path}"
    res = subprocess.call(cmd, shell=True)
    if res == 0:
        return APIResponse.success()
    return APIResponse.error(code=400)

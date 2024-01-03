import iptc
from src.utils.response import APIResponse

INPUT = "INPUT"
OUTPUT = "OUTPUT"
PREROUTING = "PREROUTING"
POSTROUTING = "POSTROUTING"
FORWARD = "FOEWARD"

FILTER = iptc.Table.FILTER
MANGLE = iptc.Table.MANGLE
RAW = iptc.Table.RAW
NAT = iptc.Table.NAT

MASQUERADE = "MASQUERADE"


def dump_table(table_name: str):
    try:
        table_info = iptc.iptc.easy.dump_table(table_name)
        return APIResponse.success(table_info)
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))
    
    
def dump_chain(table_name: str, chain_name:str):
    try:
        table_info = iptc.iptc.easy.dump_chain(table_name, chain_name)
        return APIResponse.success(table_info)
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))


def create_chain(table_name: str, chain_name: str):
    try:
        table = iptc.Table(table_name)
        if table.is_chain(chain_name):
            return APIResponse.error(400, "Error: chain already exists.")
        table.create_chain(chain_name)
        return APIResponse.success()
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))


def delete_chain(table_name: str, chain_name: str):
    try:
        table = iptc.Table(table_name)
        if table.builtin_chain(chain_name):
            return APIResponse.error(400, "Error: cannot delete builtin chain.")
        if not table.is_chain(chain_name):
            return APIResponse.error(400, "Error: chain does not exist.")
        
        table.delete_chain(chain_name)
        return APIResponse.success()
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))


def rename_chain(table_name: str, chain_name: str):
    try:
        table = iptc.Table(table_name)
        if table.builtin_chain(chain_name):
            return APIResponse.error(400, "Error: cannot rename builtin chain.")
        if not table.is_chain(chain_name):
            return APIResponse.error(400, "Error: chain does not exist.")
        
        table.rename_chain(chain_name)
        return APIResponse.success()
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))


def dump_chain(table_name: str, chain_name: str):
    try:
        chain_info = iptc.iptc.easy.dump_chain(table_name, chain_name)
        return APIResponse.success(chain_info)
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))


def create_rule(src=None, dst=None,
                in_interface=None, out_interface=None,
                jump=None, to_ports=None, 
                protocol=None,
                sport=None, dport=None,
                state=None):
    rule = iptc.Rule()
    
    if src is not None:
        rule.src = src
    if dst is not None:
        rule.dst = dst
    if in_interface is not None:
        rule.in_interface = in_interface
    if out_interface is not None:
        rule.out_interface = out_interface
    
    target = iptc.Target(rule, jump)
    
    if to_ports is not None:
        target.to_ports = to_ports
    rule.target = target
    
    if protocol is not None:
        rule.protocol = protocol
        match = iptc.Match(rule, protocol)
        
        if sport is not None:
            match.sport = sport
        if dport is not None:
            match.dport = dport
        if state is not None:
            match.state = state
        
        rule.add_match(match)

    return rule


def create_rule_from_dict(rule_dict: dict):
    rule: iptc.Rule = iptc.iptc.easy.encode_iptc_rule(rule_dict)
    return rule


# def create_rule_from_dict(rule_dict: dict):
#     rule = iptc.Rule()

#     for key, value in rule_dict.items():
#         if value is not None:
#             if key in ["src", "dst", "in_interface", "out_interface"]:
#                 setattr(rule, key, value)
#             elif key == "jump":
#                 target = iptc.Target(rule, value)
#                 to_ports = rule_dict.get("to_ports")
#                 if to_ports is not None:
#                     target.to_ports = value
#                 rule.target = target
#             elif key == "protocol":
#                 rule.protocol = value
#                 match = iptc.Match(rule, value)
#                 if rule_dict.get("sport") is not None:
#                     match.sport = rule_dict["sport"]
#                 if rule_dict.get("dport") is not None:
#                     match.dport = rule_dict["dport"]
#                 if rule_dict.get("state") is not None:
#                     match.state = rule_dict["state"]
#                 rule.add_match(match)
#     return rule
    

def append_rule(table_name: str, chain_name: str, rule_dict: dict):
    try:
        table = iptc.Table(table_name)
        if not table.is_chain(chain_name):
            return APIResponse.error(400, "Error: chain does not exist.")
        chain = iptc.Chain(table, chain_name)
        rule = create_rule_from_dict(rule_dict)
        chain.append_rule(rule)
        return APIResponse.success()
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))


def insert_rule(table_name: str, chain_name: str, rule_dict: dict):
    try:
        table = iptc.Table(table_name)
        if not table.is_chain(chain_name):
            return APIResponse.error(400, "Error: chain does not exist.")
        chain = iptc.Chain(table, chain_name)
        rule = create_rule_from_dict(rule_dict)
        chain.insert_rule(rule)
        return APIResponse.success()
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))


def delete_rule(table_name: str, chain_name: str, rule_dict: dict):
    try:
        iptc.iptc.easy.delete_rule(table_name, chain_name, rule_dict)
        return APIResponse.success()
    except iptc.IPTCError as err:
        return APIResponse.error(400, str(err))

rule_dict = {
    "src":"!1.2.3.4/255.255.255.0",
    "dst":"1.2.3.4/255.255.255.0",
    "protocol":"tcp",
    "target":MASQUERADE,
    "to_ports":"1024-65535"
}

print(dump_chain(NAT,POSTROUTING).data)
res = insert_rule(NAT, POSTROUTING, rule_dict)
print(res.code)
print(dump_chain(NAT,POSTROUTING).data)
# import os
# from ovs.db import idl as ovs_idl
# from ovsdbapp.backend.ovs_idl import connection
# from ovsdbapp.schema.open_vswitch import impl_idl

# import pprint
# from src.network_manager.idl.ovs_lib import OVSDBHelper, OVSBridge

# pp = pprint.PrettyPrinter(indent=2)

# schema_path = "/home/york/Desktop/VMManager/backend_slave/vswitch.ovsschema"
# # sock_path = "unix:/usr/local/var/run/openvswitch/db.sock"
# sock_path = "tcp:127.0.0.1:6640"

# test_ovsdb = OVSDBHelper()
# bridge = OVSBridge("york", ovsdb=test_ovsdb.ovsIdl)
# # bridges = bridge.ovsdb.db_list("Open_vSwitch").execute()
# # pp.pprint(bridges)
# # port_add = ovsbr.add_port("test777", ("type", "internal"))
# # bridge.set_port_tag("test666", 100)

# # bridge.add_port("york-t", ("type","internal"))
# # bridge.set_port_tag("york-t", 100)
# # bridge.remove_port_tag("york-t", 100)
# # ports = bridge.get_port_name_list()
# # pp.pprint(ports)
# # bridge.add_tunnel_port("remote-t", "192.168.1.2")
# bridge.delete_port("remote-t")
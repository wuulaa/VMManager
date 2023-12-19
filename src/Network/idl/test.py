# import os
# from ovs.db import idl as ovs_idl
# from ovsdbapp.backend.ovs_idl import connection
# from ovsdbapp.schema.open_vswitch import impl_idl

# import pprint
# from src.ovs_manager.idl.ovs_lib import OVSDBHelper, OVSBridge

# pp = pprint.PrettyPrinter(indent=2)

# schema_path = "/home/york/VMManger/vswitch.ovsschema"
# # sock_path = "unix:/usr/local/var/run/openvswitch/db.sock"
# sock_path = "tcp:127.0.0.1:6640"

# test_ovsdb = OVSDBHelper(sock_path, schema_path)
# ovsbr = OVSBridge("test", ovsdb=test_ovsdb.ovsIdl)
# # bridges = ovsbr.ovsdb.db_list("Open_vSwitch").execute()
# # pp.pprint(bridges)
# # port_add = ovsbr.add_port("test777", ("type", "internal"))
# ovsbr.set_port_tag("test666", 100)
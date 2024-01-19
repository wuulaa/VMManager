import collections

from ovs.db import idl
from ovsdbapp.backend.ovs_idl import connection
from ovsdbapp.backend.ovs_idl.command import BaseCommand
from ovsdbapp.schema.open_vswitch import impl_idl
from src.utils.config import CONF

FAILMODE_SECURE = 'secure'
FAILMODE_STANDALONE = 'standalone'

OVS_DATAPATH_SYSTEM = 'system'
TYPE_GRE = 'gre'
TYPE_VXLAN = 'vxlan'
VXLAN_UDP_PORT = 4789
TYPE_GRE_IP6 = 'ip6gre'
SCHEMA_PATH = CONF["ovs"]["schemapath"]
SOCK_PATH = CONF["ovs"]["sockpath"]


class OVSDBHelper:
    def __init__(self, sock: str = SOCK_PATH, schema_path: str = SCHEMA_PATH):
        schema_helper: idl.SchemaHelper = idl.SchemaHelper(schema_path)
        schema_helper.register_all()

        ovs_idl = idl.Idl(sock, schema_helper)
        ovs_conn = connection.Connection(idl=ovs_idl, timeout=10)
        self.ovsIdl = impl_idl.OvsdbIdl(ovs_conn)


class BaseOVS:
    def __init__(self, ovsdb: impl_idl.OvsdbIdl):
        self.ovsdb = ovsdb

    def _execute(self, cmd: BaseCommand, check_error=False, log_errors=True):
        try:
            return cmd.execute(check_error=check_error, log_errors=log_errors)
        except Exception as e:
            print(e)
            if check_error:
                raise e

    def add_bridge(self, bridge_name: str, datapath_type=OVS_DATAPATH_SYSTEM, secure_mode=False):
        ovs_bridge = OVSBridge(bridge_name, self.ovsdb)
        ovs_bridge.create(secure_mode=secure_mode)
        return ovs_bridge

    def delete_bridge(self, bridge_name: str):
        self.ovsdb.del_br(bridge_name).execute()

    def bridge_exists(self, bridge_name: str):
        cmd = self.ovsdb.db_get('Bridge', bridge_name, 'name')
        return bool(cmd.execute(check_error=False, log_errors=False))

    def port_exists(self, port_name: str):
        cmd = self.ovsdb.db_get('Port', port_name, 'name')
        return bool(cmd.execute(check_error=False, log_errors=False))

    def get_bridge_for_interface(self, interface):
        return self.ovsdb.iface_to_br(interface).execute()

    def get_bridges(self):
        return self.ovsdb.list_br().execute()

    def get_bridge_external_bridge_id(self, bridge, check_error=False,
                                      log_errors=True):
        return self._execute(self.ovsdb.br_get_external_id(bridge, 'bridge-id'),
                             check_error=check_error, log_errors=log_errors)

    def set_db_attribute(self, table_name: str, record, column, value,
                         check_error=False, log_errors=True):
        self._execute(
            self.ovsdb.db_set(table_name, record, (column, value)),
            check_error=check_error, log_errors=log_errors)

    def clear_db_attribute(self, table_name, record, column):
        self.ovsdb.db_clear(table_name, record, column).execute()

    def db_get_val(self, table, record, column, check_error=False,
                   log_errors=True):
        return self._execute(
            self.ovsdb.db_get(table, record, column),
            check_error=check_error, log_errors=log_errors)

    @property
    def config(self):
        """A dict containing the only row from the root Open_vSwitch table

        This row contains several columns describing the Open vSwitch install
        and the system on which it is installed. Useful keys include:
            datapath_types: a list of supported datapath types
            iface_types: a list of supported interface types
            ovs_version: the OVS version
        """
        return self.ovsdb.db_list("Open_vSwitch").execute()[0]


class OVSBridge(BaseOVS):

    def __init__(self,
                 br_name: str,
                 ovsdb: impl_idl.OvsdbIdl,
                 datapath_type=OVS_DATAPATH_SYSTEM):
        super().__init__(ovsdb)
        self.bridge_name = br_name
        self.datapath_type = datapath_type

    def set_controller(self, controller):
        self.ovsdb.set_controller(self.bridge_name, controller).execute(check_error=True)

    def del_controller(self):
        self.ovsdb.del_controller(self.bridge_name).execute(check_error=True)

    def get_controller(self):
        return self.ovsdb.get_controller(self.bridge_name).execute(check_error=True)

    def _set_bridge_fail_mode(self, mode):
        self.ovsdb.set_fail_mode(self.bridge_name, mode).execute(check_error=True)

    def set_secure_mode(self):
        self._set_bridge_fail_mode(FAILMODE_SECURE)

    def set_standalone_mode(self):
        self._set_bridge_fail_mode(FAILMODE_STANDALONE)

    def create(self, secure_mode: bool = False):
        # create and open a transaction
        with self.ovsdb.transaction() as txn:
            txn.add(self.ovsdb.add_br(self.bridge_name, datapath_type=self.datapath_type))
            # TODO: add protocol and set mac table config
            # txn.add(self.ovsdb.db_set('Bridge', self.bridge_name))
            if secure_mode:
                txn.add(self.ovsdb.set_fail_mode(self.bridge_name,FAILMODE_SECURE))

    def destroy(self):
        self.delete_bridge(self.bridge_name)

    def add_port(self, port_name: str, *interface_attribute_tuples):
        with self.ovsdb.transaction() as txn:
            txn.add(self.ovsdb.add_port(self.bridge_name, port_name))
            if interface_attribute_tuples:
                txn.add(self.ovsdb.db_set('Interface',
                                          port_name,
                                          *interface_attribute_tuples))
        # TODO: return self.get_port_ofport(port_name)

    def replace_port(self, port_name: str, *interface_attribute_tuples):
        self.ovsdb.del_port(port_name).execute()
        with self.ovsdb.transaction() as txn:
            txn.add(self.ovsdb.add_port(self.bridge_name, port_name,may_exist=False))
            if interface_attribute_tuples:
                txn.add(self.ovsdb.db_set('Interface', port_name,
                                          *interface_attribute_tuples))

    def delete_port(self, port_name: str):
        self.ovsdb.del_port(port_name, self.bridge_name).execute()

    def add_tunnel_port(self, port_name: str,
                        remote_ip: str,
                        local_ip: str = None,
                        tunnel_type=TYPE_VXLAN,
                        vxlan_udp_port=VXLAN_UDP_PORT,
                        dont_fragment=True,
                        tunnel_csum=False,
                        tos=None):
        if tunnel_type == TYPE_GRE:
            # tunnel_type = get_gre_tunnel_port_type(remote_ip, local_ip)
            pass
        attrs = [('type', tunnel_type)]

        options = collections.OrderedDict()
        # vxlan_uses_custom_udp_port = (
        #     tunnel_type == TYPE_VXLAN and vxlan_udp_port != VXLAN_UDP_PORT)
        # if vxlan_uses_custom_udp_port:
        #     options['dst_port'] = str(vxlan_udp_port)
        # options['df_default'] = str(dont_fragment).lower()
        options['remote_ip'] = remote_ip
        if local_ip is not None:
            options['local_ip'] = local_ip
        # options['in_key'] = 'flow'
        # options['out_key'] = 'flow'

        # if not self.is_hw_offload_enabled:
        #     options['egress_pkt_mark'] = '0'
        if tunnel_csum:
            options['csum'] = str(tunnel_csum).lower()
        if tos:
            options['tos'] = str(tos)
        if tunnel_type == TYPE_GRE_IP6:
            options['packet_type'] = 'legacy_l2'
        attrs.append(('options', options))

        return self.add_port(port_name, *attrs)

    def add_patch_port(self, local_name: str, remote_name: str):
        attrs = [('type', 'patch'),
                 ('options', {'peer': remote_name})]
        return self.add_port(local_name, *attrs)

    def get_interface_name_list(self):
        return self.ovsdb.list_ifaces(self.bridge_name).execute(check_error=True)

    def get_port_name_list(self):
        return self.ovsdb.list_ports(self.bridge_name).execute(check_error=True)

    def get_port_stats(self, port_name: str):
        return self.db_get_val("Interface", port_name, "statistics")

    def get_ports_attributes(self, table,
                             columns=None,
                             ports=None,
                             check_error=True,
                             log_errors=True,
                             if_exists=False):
        port_names = ports or self.get_port_name_list()
        if not port_names:
            return []
        return (self.ovsdb.db_list(table, port_names, columns=columns,if_exists=if_exists).
                execute(check_error=check_error, log_errors=log_errors))

    def get_port_tag_dict(self):
        """Get a dict of port names and associated vlan tags.
                e.g. the returned dict is of the following form::
                    {u'int-br-eth2': [],
                     u'patch-tun': [],
                     u'qr-76d9e6b6-21': 1,
                     u'tapce5318ff-78': 1,
                     u'tape1400310-e6': 1}

                The TAG ID is only available in the "Port" table and is not available
                in the "Interface" table queried by the get_vif_port_set() method.

                """
        results = self.get_ports_attributes(
            'Port', columns=['name', 'tag'], if_exists=True)
        return {p['name']: p['tag'] for p in results}

    def delete_ports(self, all_ports=False):
        if all_ports:
            port_names = self.get_port_name_list()
        else:
            port_names = self.get_port_name_list()
            # port_names = (port.port_name for port in self.get_vif_ports())
        for port_name in port_names:
            self.delete_port(port_name)

    def set_port_tag(self, port_name: str, tag: str):
        self.ovsdb.db_set('Port', port_name, ('tag', tag)).execute()
    
    def remove_port_tag(self, port_name: str, tag: str):
        self.ovsdb.db_remove('Port', port_name, 'tag', tag).execute()

    def set_port_type(self, port_name: str, port_type: str):
        self.ovsdb.db_set('Interface', port_name, ('type', port_type)).execute()


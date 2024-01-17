from __future__ import annotations

from typing import Any, List
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, String, Enum
from sqlalchemy import SmallInteger, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from src.utils.sqlalchemy.model import Base
from src.utils.sqlalchemy import enginefacade

class Network(Base):
    __tablename__ = "network"
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="network UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="network name")
    address: Mapped[str] = mapped_column(String(64),
                                        unique=True,
                                        comment="network address ,eg: 1.2.3.4/24")
    interfaces: Mapped[List["Interface"]] = relationship(back_populates="network")
    
    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address
        self.uuid = self._gen_uuid()
   



class Interface(Base):
    __tablename__ = "interface"
    name: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="port name")
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="interface UUID")
    
    interface_type: Mapped[str] = mapped_column(Enum("direct", "network"),
                                                default="direct",
                                                comment="interface type, currently we only support ovs direct port")
    
    status: Mapped[str] = mapped_column(Enum("unbound", "bound_unuse", "bound_in_use"),
                                        default="unbound",
                                        comment="status of a interface")
    
    mac: Mapped[str] = mapped_column(String(64),
                                      nullable=True,
                                      unique=True,
                                      comment="mac address")
    
    ip_address: Mapped[str] = mapped_column(String(64),
                                            nullable=True,
                                            unique=False,
                                            comment="ip address bond to the interface, could be null if net set yet")
    
    gateway: Mapped[str] = mapped_column(String(64),
                                            nullable=True,
                                            unique=False,
                                            comment="ip gateway bond to the interface, could be null if net set yet")
    
    xml: Mapped[str] = mapped_column(String(64),
                                     nullable=True,
                                     comment="xml string of a NIC/interface")
    
    network_uuid: Mapped[str] = mapped_column(String(64),
                                              ForeignKey('network.uuid'),
                                              comment="UUID of the network this interface belongs to")
    
    port_uuid: Mapped[str] = mapped_column(String(64),
                                           nullable=True,
                                           comment="UUID of the ovs port this interface owns. This could be used to get the source name")
    
    guest_uuid: Mapped[str] = mapped_column(String(64),
                                            nullable=True,
                                            comment="UUID of the guest VM this interface belongs to")
    
    slave_uuid: Mapped[str] = mapped_column(String(64),
                                            nullable=True,
                                            comment="UUID of the slave node this interface is bound to")
    
    ip_modified: Mapped[Boolean] = mapped_column(Boolean,
                                             default=False,
                                             comment="If interface ip is modified when domain is shutdown")
    
    network: Mapped["Network"] = relationship(back_populates="interfaces")
    
    def __init__(self,
                 name: str,
                 network_uuid: str,
                 ip_address: str,
                 gateway: str,
                 mac: str = None,
                 inerface_type: str = "direct"
                 ):
        if ip_address:
            self.name = name
            self.uuid = self._gen_uuid()
            self.network_uuid = network_uuid
            self.interface_type = inerface_type
            self.ip_address = ip_address
            self.gateway = gateway
            if mac is not None:
                self.mac = mac
    

    
# class OVSBridge(Base):
#     __tablename__ = "ovs_bridge"
#     uuid: Mapped[str] = mapped_column(String(64),
#                                       unique=True,
#                                       comment="OVS bridge UUID")
    
#     name: Mapped[str] = mapped_column(String(64),
#                                       comment="OVS bridge name")
    
#     slave_uuid: Mapped[str] = mapped_column(String(64),
#                                       comment="slave node uuid")
    
#     ports: Mapped[List["OVSPort"]] = relationship(back_populates="bridge",
#                                                   cascade="all, delete-orphan")
    
#     def __init__(self,
#                  name: str,
#                  slave_uuid: str,
#                  ):
        
#         self.uuid = self._gen_uuid()
#         self.name = name
#         self.slave_uuid = slave_uuid
    

class OVSPort(Base):
    __tablename__ = "ovs_port"
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="OVS port UUID")
    
    name: Mapped[str] = mapped_column(String(64),
                                      comment="OVS port name")
    
    vlan_tag: Mapped[int] = mapped_column(Integer,
                                          nullable=True,
                                          comment="OVS port tag")
    
    slave_uuid: Mapped[str] = mapped_column(String(64),
                                             comment="The UUID of slave this port belongs to.")
    
    interface_uuid: Mapped[str] = mapped_column(String(64),
                                             comment="The UUID of interface this port is bound to.")
    
    port_type: Mapped[str] = mapped_column(Enum("internal", "vxlan"),
                                           default="internal",
                                           comment="ovs_port type, could be a vxlan port or a internal port")
    
    remote_ip: Mapped[str] = mapped_column(String(64),
                                           nullable= True,
                                           comment="remote ip addr if port is a vxlan port")


    def __init__(self,
                 name: str,
                 interface_uuid: str,
                 port_type: str = "internal",
                 remote_ip: str = None,
                 vlan_tag: str = None
                 ):
        
        self.uuid = self._gen_uuid()
        self.name = name
        self.interface_uuid = interface_uuid
        self.port_type = port_type
        if port_type == "vxlan" and remote_ip is not None:
            self.remote_ip = remote_ip
        if vlan_tag:
            self.vlan_tag = vlan_tag


Base.metadata.create_all(enginefacade.get_engine())
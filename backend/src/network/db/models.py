from __future__ import annotations

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, String, Enum
from sqlalchemy import SmallInteger, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from backend.src.utils.sqlalchemy.model import Base
from backend.src.utils.sqlalchemy import enginefacade

class Network(Base):
    __tablename__ = "network"
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="network UUID")



class Interface(Base):
    __tablename__ = "interface"
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="interface UUID")
    interface_type: Mapped[str] = mapped_column(Enum("direct", "network"),
                                      comment="Interface UUID")
    
    mac: Mapped[str] = mapped_column(String(64),
                                      nullable=True,
                                      unique=True,
                                      comment="mac address")
    source_uuid: Mapped[str] = mapped_column(String(64),
                                      nullable=False,
                                      unique=True,
                                      comment="interface source, mapped to a network")
    model_type: Mapped[str] = mapped_column(String(64),
                                            default="virtio",
                                            comment="interface model type")
    xml: Mapped[str] = mapped_column(String(64),
                                     comment="xml string of a NIC/interface")
    network_uuid: Mapped[str] = mapped_column(String(64),
                                      comment="UUID of the network this interface belongs to")
    
class OVSBridge(Base):
    __tablename__ = "ovs_bridge"
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="OVS bridge UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      comment="OVS bridge name")
    ports: Mapped[List["OVSPort"]] = relationship(back_populates="ovs_bridge",
                                                   cascade="all, delete-orphan")
    

class OVSPort(Base):
    __tablename__ = "ovs_port"
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="OVS port UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      comment="OVS port name")
    vlan_tag: Mapped[str] = mapped_column(String(64),
                                          nullable=True,
                                          comment="OVS port tag")
    bridge_uuid: Mapped[str] = mapped_column(String(64),
                                             comment="The UUID of ovs bridge this port belongs to")
    bridge: Mapped["OVSBridge"] = relationship(back_populates="ports")



Base.metadata.create_all(enginefacade.get_engine())
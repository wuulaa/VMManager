from __future__ import annotations

from typing import Any, List
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, String
from sqlalchemy import SmallInteger, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from src.utils.sqlalchemy.model import Base
from src.utils.sqlalchemy import enginefacade


# status = {
#     0:"nostate",
#     1:"running",
#     2:"blocked",
#     3:"paused",
#     4:"shutdown",
#     5:"shutoff",
#     6:"crashed",
#     7:"pmsuspended"
# }

class Guest(Base):
    __tablename__ = 'guest'
    
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Guest UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=False,
                                      comment="Guest name")
    user_uuid: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=False,
                                      comment="User UUID")
    slave_name: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=False,
                                      comment="Node name")
    title: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest title")
    description: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest description")
    status: Mapped[str] = mapped_column(String(64),
                                     default=0,
                                     comment="Guest status")
    architecture: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest architecture")
    cpu: Mapped[int] = mapped_column(Integer,
                                     default=0,
                                     nullable=True,
                                     comment="CPU count")
    max_cpu: Mapped[int] = mapped_column(Integer,
                                     default=0,
                                     nullable=True,
                                     comment="Max CPU count")
    memory: Mapped[int] = mapped_column(Integer,
                                        default=0,
                                        nullable=True,
                                        comment="Memory size(MB)")
    max_memory: Mapped[int] = mapped_column(Integer,
                                        default=0,
                                        nullable=True,
                                        comment="Max Memory size(MB)")
    boot_option: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest boot option, mapped to a volume")
    spice_address: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest SPICE address")
    vnc_address: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest VNC address, including ip, port and passwd")
    parent_uuid: Mapped[str] = mapped_column(String(64),
                                             nullable=True,
                                             comment="parent guest uuid")
    children_list: Mapped[str] = mapped_column(String(64),
                                               nullable=True,
                                               comment="children guest uuid list")
    backups_list: Mapped[str] = mapped_column(String(64),
                                              nullable=True,
                                              comment="backups uuid list, including ip, port and passwd")
    
    def __init__(self,
                 uuid,
                 name,
                 user_uuid,
                 slave_name,
                 title: str = None,
                 description: str = None,
                 status: str = "running",
                 architecture: str = "x86",
                 cpu: int = None,
                 max_cpu: int = None,
                 memory: int = None,
                 max_memory: int = None,
                 boot_option: str = None,
                 spice_address: str = None,
                 vnc_address: str = None,
                 parent_uuid: str = None,
                 children_list: str = None,
                 backups_list: str = None):
        self.uuid = uuid
        self.name = name
        self.user_uuid = user_uuid
        self.slave_name = slave_name
        self.title = title
        self.description = description
        self.status = status
        self.architecture = architecture
        self.cpu = cpu
        self.max_cpu = max_cpu
        self.memory = memory
        self.max_memory = max_memory
        self.boot_option = boot_option
        self.spice_address = spice_address
        self.vnc_address= vnc_address
        self.parent_uuid = parent_uuid
        self.children_list = children_list
        self.backups_list = backups_list 

class Slave(Base):
    __tablename__ = 'slave'
    
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Slave UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Slave name")
    address: Mapped[str] = mapped_column(String(64),
                                         unique=True,
                                         comment="Slave address, including ip and port")

    def __init__(self, name: str, address: str):
        self.name = name
        self.address = address
        self.uuid = self._gen_uuid()
    
Base.metadata.create_all(enginefacade.get_engine())
    
    
from __future__ import annotations

from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, String
from sqlalchemy import SmallInteger, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from backend.src.utils.sqlalchemy.model import Base
from backend.src.utils.sqlalchemy import enginefacade


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
    status: Mapped[int] = mapped_column(Integer,
                                     default=0,
                                     comment="Guest status")
    architecture: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest architecture")
    cpu: Mapped[int] = mapped_column(Integer,
                                     default=0,
                                     comment="CPU count")
    max_cpu: Mapped[int] = mapped_column(Integer,
                                     default=0,
                                     comment="Max CPU count")
    memory: Mapped[int] = mapped_column(Integer,
                                        default=0,
                                        comment="Memory size(MB)")
    max_memory: Mapped[int] = mapped_column(Integer,
                                        default=0,
                                        comment="Max Memory size(MB)")
    boot_option: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      comment="Guest boot option, mapped to a volume")
    spice_address: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest SPICE address")
    vnc_address: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Guest VNC address")
    parent_uuid: Mapped[str] = mapped_column(String(64),
                                             comment="parent guest uuid")
    children_list: Mapped[str] = mapped_column(String(64),
                                               comment="children guest uuid list")
    backups_list: Mapped[str] = mapped_column(String(64),
                                              comment="backups uuid list")


class Slave(Base):
    __tablename__ = 'slave'
    
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Slave UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=False,
                                      comment="Slave name")

    
Base.metadata.create_all(enginefacade.get_engine())
    
    
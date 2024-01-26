from __future__ import annotations

import importlib
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy import Boolean, String
from sqlalchemy import SmallInteger, Integer
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from src.utils.sqlalchemy import enginefacade
from src.utils.sqlalchemy.model import Base
from src.volume.common import config


CONF = config.CONF
if (CONF['volume']['provider'].lower() == 'rbd'):
    volume_settings = config.RbdSettings()
else:
    volume_settings = config.LibvirtSettings()

xmlbuilder_path = volume_settings.xml_builder
xmlbuilder_module_name, xmlbuilder_name = xmlbuilder_path.rsplit('.', 1)
xmlbuilder_module = importlib.import_module(xmlbuilder_module_name)
xml_builder = getattr(xmlbuilder_module, xmlbuilder_name)


class Pool(Base):
    __tablename__ = 'pool'

    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="Pool UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Pool name")
    status: Mapped[bool] = mapped_column(Boolean,
                                         default=False,
                                         comment="The active state of the pool"
                                                 "{down: 0, up: 1}")
    allocation: Mapped[int] = mapped_column(Integer,
                                            default=0,
                                            comment="Total pool capacity (MB)")
    usage: Mapped[int] = mapped_column(Integer,
                                       default=0,
                                       comment="Used capacity (MB)")
    owner: Mapped[str] = mapped_column(String(64),
                                       comment="The user who owns this pool")

    volumes: Mapped[List["Volume"]] = relationship(back_populates="pool",
                                                   cascade="all, delete-orphan")

    def __init__(self, name: str = None, allocation: int = 0, owner: str = None):
        if name is not None:
            self.name = name
            self.allocation = allocation
            self.owner = owner

            self.usage = 0
            self.uuid = self._gen_uuid()


class Volume(Base):
    __tablename__ = 'volume'

    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="Volume UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Volume name")
    status: Mapped[int] = mapped_column(SmallInteger,
                                        default=0,
                                        comment="The active state of the volume")
    allocation: Mapped[int] = mapped_column(Integer,
                                            default=20480,
                                            comment="Total volume capacity (MB)")
    parent_uuid: Mapped[str] = mapped_column(String(64),
                                             ForeignKey('volume.uuid'),
                                             nullable=True,
                                             comment="UUID of the cloned volume")
    pool_uuid: Mapped[str] = mapped_column(String(64),
                                           ForeignKey('pool.uuid'),
                                           nullable=False,
                                           comment="The UUID of pool"
                                                   "where volume resides in")
    guest_uuid: Mapped[str] = mapped_column(String(64),
                                            index=True,
                                            nullable=True,
                                            comment="The UUID of guest"
                                                    "using this volume")
    dev_order: Mapped[int] = mapped_column(SmallInteger,
                                           default=None,
                                           nullable=True,
                                           comment="The order of device")

    pool: Mapped["Pool"] = relationship(back_populates="volumes")

    snapshots: Mapped[List["Snapshot"]] = relationship(back_populates="volume",
                                                       cascade="all, delete-orphan") 

    parent: Mapped["Volume"] = relationship(back_populates="children",
                                            remote_side=[uuid])

    children: Mapped[List["Volume"]] = relationship(back_populates="parent",
                                                    cascade="all, delete-orphan")

    def __init__(self,
                 pool_uuid: str = None,
                 name: str = None,
                 allocation: int = 20480,
                 parent_uuid: str = None,
                 guest_uuid: str = None,
                 dev_order: int = None):
        if (name is not None and pool_uuid is not None):
            self.name = name
            self.pool_uuid = pool_uuid
            self.allocation = allocation
            self.parent_uuid = parent_uuid
            self.guest_uuid = guest_uuid
            self.dev_order = dev_order

            self.uuid = self._gen_uuid()

    def get_device(self):
        return xml_builder().construct(volume_name=self.name,
                                       dev_order=self.dev_order)

    def get_xml_string(self):
        return self.get_device().get_xml_string()


class Snapshot(Base):
    __tablename__ = 'snapshot'

    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      comment="Snapshot UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      nullable=False,
                                      comment="Snapshot name")
    volume_uuid: Mapped[str] = mapped_column(String(64),
                                             ForeignKey('volume.uuid'),
                                             comment="UUID of the snapshotted volume")
    is_temp: Mapped[bool] = mapped_column(Boolean,
                                          nullable=False,
                                          comment="Whether it was created "
                                                  "temporarily due to cloning")

    volume: Mapped["Volume"] = relationship(back_populates="snapshots")

    def __init__(self,
                 volume_uuid: str,
                 snap_name: str,
                 is_temp: bool):
        if (volume_uuid is None or snap_name is None):
            raise Exception('volume_uuid or snapshot name cannot be empty')
        self.volume_uuid = volume_uuid
        self.name = snap_name
        self.is_temp = is_temp

        self.uuid = self._gen_uuid()


Base.metadata.create_all(enginefacade.get_engine())

from __future__ import annotations

import importlib
from typing import List, Optional
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import SmallInteger, Integer
from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from .engine import engine


# model 基类
class StorageBase(DeclarativeBase):
    # 数据表配置
    __table_args__ = {'mysql_engine': 'InnoDB',     # 使用 InnoDB 引擎
                      'mysql_charset': 'utf8mb4'}   # 编码格式


class Pool(StorageBase):
    __tablename__ = 'pool'

    id: Mapped[str] = mapped_column(String(64),
                                    primary_key=True,
                                    comment="Pool UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Pool name")
    status: Mapped[bool] = mapped_column(Boolean,
                                         default=False,
                                         comment="The active state of the pool, {down: 0, up: 1}")
    allocation: Mapped[int] = mapped_column(Integer,
                                            default=0,
                                            comment="Total pool capacity (MB)")
    usage: Mapped[int] = mapped_column(Integer,
                                       default=0,
                                       comment="Used capacity (MB)")
    owner: Mapped[str] = mapped_column(String(64),
                                       comment="The user who owns this pool")
    volumes: Mapped[List["Volume"]] = relationship(
        back_populates="pool", cascade="all, delete-orphat"
    )

    def __init__(self, name=None, allocation=None, owner=None):
        if name is not None:
            self.name = name
            self.allocation = allocation
            self.owner = owner

            self.usage = 0
            self.id = self._gen_uuid()


class Volume(StorageBase):
    __tablename__ = 'volume'

    id: Mapped[str] = mapped_column(String(64),
                                    primary_key=True,
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
    pool_id: Mapped[str] = mapped_column(String(64),
                                         ForeignKey('pool.id'),
                                         nullable=False,
                                         comment="The UUID of pool where volume resides")
    vm_id: Mapped[str] = mapped_column(String(64),
                                       comment="The UUID of VM using this volume")
    dev_order: Mapped[int] = mapped_column(SmallInteger,
                                           default=0,
                                           comment="The order of device")
    pool: Mapped["Pool"] = relationship(back_populates="volumes")

    def __init__(self,
                 pool_id: str = None,
                 name: str = None,
                 allocation: int = 20480,
                 vm_uuid: str = None,
                 dev_order: int = 0):
        if (name is not None and pool_id is not None):
            self.name = name
            self.pool_id = pool_id
            self.allocation = allocation
            self.vm_id = vm_uuid
            self.dev_order = dev_order

            self.id = self._gen_uuid()

    # def _get_device(self):
    #     return xml_builder().construct(volume_name=self.name,
    #                                    dev_order=self.dev_order)

    # def get_xml_string(self):
    #     return self._get_device().get_xml_string()


StorageBase.metadata.create_all(engine)

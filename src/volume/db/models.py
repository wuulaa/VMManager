from __future__ import annotations

import importlib
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import SmallInteger, Integer
from sqlalchemy.orm import declarative_base

from src.utils.generator import UUIDGenerator
from src.volume.common import config


# 获取数据库引擎
engine = enginefacade.get_legacy_facade().get_engine()

# 提供增删改查的能力
BASE = declarative_base()


# model 基类
class StorageBase(models.TimestampMixin,
                  models.ModelBase):
    # 数据表配置
    __table_args__ = {'mysql_engine': 'InnoDB',     # 使用 InnoDB 引擎
                      'mysql_charset': 'utf8mb4'}   # 编码格式

    deleted_at = Column(DateTime)
    deleted = Column(Boolean, default=False)
    metadata = None

    @staticmethod
    def delete_values():
        return {'deleted': True, 'deleted_at': timeutils.utcnow()}

    def delete(self, session):
        """Delete this object."""
        updated_values = self.delete_values()
        updated_values['updated_at'] = self.updated_at
        self.update(updated_values)
        self.save(session=session)
        del updated_values['updated_at']
        return updated_values

    def _gen_uuid(self):
        return UUIDGenerator.get_uuid()

    @classmethod
    def to_db_object(cls, values: dict) -> Pool:
        pool = Pool()
        attributes = vars(values)
        for key, value in attributes.items():
            if key in cls.__table__.columns.keys():
                pool[key] = value

        return pool

    def to_dict(self) -> dict:
        dict = {}
        for key in self.keys():
            if self[key] is not None:
                dict[key] = self[key]

        return dict


class Pool(BASE, StorageBase):
    __tablename__ = 'pool'

    id = Column(String(64),
                primary_key=True,
                comment="Pool UUID")
    name = Column(String(64),
                  unique=True,
                  nullable=False,
                  comment="Pool name")
    status = Column(Boolean,
                    default=False,
                    comment="The active state of the pool, {down: 0, up: 1}")
    allocation = Column(Integer,
                        default=0,
                        comment="Total pool capacity (MB)")
    usage = Column(Integer,
                   default=0,
                   comment="Used capacity (MB)")
    owner = Column(String(64),
                   comment="The user who owns this pool")

    def __init__(self, name=None, allocation=None, owner=None):
        if name is not None:
            self.name = name
            self.allocation = allocation
            self.owner = owner

            self.usage = 0
            self.id = self._gen_uuid()


CONF = config.CONF

# 通过配置信息动态加载 xmlbuilder
xml_builder_path = CONF[CONF.provider].xml_builder
xml_builder_module_name, xml_builder_name = xml_builder_path.rsplit('.', 1)
xml_builder_module = importlib.import_module(xml_builder_module_name)
xml_builder = getattr(xml_builder_module, xml_builder_name)


class Volume(BASE, StorageBase):
    __tablename__ = 'volume'

    id = Column(String(64),
                primary_key=True,
                comment="Volume UUID")
    name = Column(String(64),
                  unique=True,
                  nullable=False,
                  comment="Volume name")
    status = Column(SmallInteger,
                    default=0,
                    comment="The active state of the volume")
    allocation = Column(Integer,
                        default=20480,
                        comment="Total volume capacity (MB)")
    pool_id = Column(String(64),
                     ForeignKey('pool.id'),
                     nullable=False,
                     comment="The UUID of pool where volume resides")
    vm_id = Column(String(64),
                   comment="The UUID of vm which using this volume")

    dev_order = Column(SmallInteger,
                       default=0,
                       comment="The order of device")

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

    def _get_device(self):
        return xml_builder().construct(volume_name=self.name,
                                       dev_order=self.dev_order)

    def get_xml_string(self):
        return self._get_device().get_xml_string()


BASE.metadata.create_all(engine)

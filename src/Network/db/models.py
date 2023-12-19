from __future__ import annotations
from oslo_db.sqlalchemy import enginefacade
from oslo_db.sqlalchemy import models
from oslo_utils import timeutils
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Boolean, DateTime, String
from sqlalchemy import SmallInteger, Integer
from sqlalchemy.orm import declarative_base

# get the database engine
engine = enginefacade.get_legacy_facade().get_engine()

# get CRUD capabilities
BASE = declarative_base()


class StorageBase(models.TimestampMixin,
                  models.ModelBase):
    # 数据表配置
    __table_args__ = {'mysql_engine': 'InnoDB',     # 使用 InnoDB 引擎
                      'mysql_charset': 'utf8mb4'}   # 编码格式


class Bridge(BASE, StorageBase):
    __tablename__ = 'bridge'

    id = Column(String(64),
                primary_key=True,
                comment="Bridge UUID")

    name = Column(String(64),
                  unique=True,
                  nullable=False,
                  comment="Bridge name")

    def __init__(self, name=None):
        if name is not None:
            self.name = name


class Port(BASE, StorageBase):
    __tablename__ = "port"

    def __init__(self, name=None):
        if name is not None:
            self.name = name

    id = Column(String(64),
                primary_key=True,
                comment="Port UUID")

    name = Column(String(64),
                  unique=True,
                  nullable=False,
                  comment="Port name")

    mac = Column(String(64),
                 comment="Mac address of the port")

    type = Column(String(64),
                  comment="The type of ovs port")

    tag = Column(String(64),
                 comment="Vlan tag")


from __future__ import annotations

from typing import List
from sqlalchemy import Integer

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from . import enginefacade
from src.utils.generator import UUIDGenerator
from src.utils.serializable import JsonSerializable
import datetime

# model 基类
class Base(DeclarativeBase, JsonSerializable):
    # 数据表配置
    __table_args__ = {'mysql_engine': 'InnoDB',     # 使用 InnoDB 引擎
                      'mysql_charset': 'utf8mb4'}   # 编码格式

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True,
                                    comment="Primary Key")

    def _as_dict(self):
        return JsonSerializable._as_dict(self, self.to_dict().keys())

    def _gen_uuid(self):
        return UUIDGenerator.get_uuid()

    def to_dict(self) -> dict:
        dict = {}
        for field in self.__table__.columns.keys():
            if field in self.__dict__ and self.__dict__[field] is not None:
                if isinstance(self.__dict__[field], datetime.datetime):
                    dict[field] = str(self.__dict__[field])
                else:
                    dict[field] = self.__dict__[field]
        return dict


Base.metadata.create_all(enginefacade.get_engine())

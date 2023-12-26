from __future__ import annotations

from typing import List
from sqlalchemy import Integer

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from . import enginefacade
from backend.src.utils.generator import UUIDGenerator


# model 基类
class Base(DeclarativeBase):
    # 数据表配置
    __table_args__ = {'mysql_engine': 'InnoDB',     # 使用 InnoDB 引擎
                      'mysql_charset': 'utf8mb4'}   # 编码格式

    _field_list: List = None

    id: Mapped[int] = mapped_column(Integer,
                                    primary_key=True,
                                    autoincrement=True,
                                    comment="Primary Key")

    def _gen_uuid(self):
        return UUIDGenerator.get_uuid()

    def get_field_list(self) -> List:
        if self._field_list is None:
            self._field_list = [
                column.name for column in self.__table__.columns]
        return self._field_list

    def to_dict(self) -> dict:
        dict = {}
        for field in self.get_field_list():
            if field in self.__dict__ and self.__dict__[field] is not None:
                dict[field] = self.__dict__[field]
        return dict


Base.metadata.create_all(enginefacade.get_engine())

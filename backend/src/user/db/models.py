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


class User(Base):
    __tablename__ = 'user'
    
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="User UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="User name")
    password: Mapped[str] = mapped_column(String(64),
                                         unique=True,
                                         nullable=False,
                                         comment="User password, store encrypted str")
    is_admin: Mapped[bool] = mapped_column(Boolean(),
                                           default=False,
                                           comment="whether a user is an admin")
    token: Mapped[str] = mapped_column(String(512),
                                       nullable=True,
                                       unique=True,
                                       comment="token for jwt")
    state: Mapped[str] = mapped_column(Enum("online", "offline"),
                                       default="offline",
                                       comment="user state, online or offline")
    

    def __init__(self, name: str, password: str, is_admin: bool):
        self.name = name
        self.password = password
        self.is_admin = is_admin
        self.state = "offline"
        self.uuid = self._gen_uuid()
    
Base.metadata.create_all(enginefacade.get_engine())
    
    
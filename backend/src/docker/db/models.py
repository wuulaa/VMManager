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

class DockerGuest(Base):
    __tablename__ = 'docker_guest'
    
    uuid: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Docker Guest UUID")
    container_id: Mapped[str] = mapped_column(String(64),
                                      unique=True,
                                      nullable=False,
                                      comment="Docker container UUID")
    name: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=False,
                                      comment="Container name")
    user_uuid: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=False,
                                      comment="User UUID")
    slave_name: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=False,
                                      comment="Slave name")

    status: Mapped[str] = mapped_column(String(64),
                                     default=0,
                                     comment="Guest status")
    
    cpu_shares: Mapped[int] = mapped_column(Integer,
                                     default=0,
                                     nullable=True,
                                     comment="Container CPU shares")
    # max_cpu: Mapped[int] = mapped_column(Integer,
    #                                  default=0,
    #                                  nullable=True,
    #                                  comment="Max CPU count")
    memory_limit: Mapped[str] = mapped_column(String,
                                        default="512mb",
                                        nullable=True,
                                        comment="Memory size")
    # max_memory: Mapped[int] = mapped_column(Integer,
    #                                     default=0,
    #                                     nullable=True,
    #                                     comment="Max Memory size(KB)")
    vnc_address: Mapped[str] = mapped_column(String(64),
                                      unique=False,
                                      nullable=True,
                                      comment="Docker VNC address, including ip, port and passwd")
    
    
    def __init__(self,
                 uuid,
                 container_id,
                 name,
                 user_uuid,
                 slave_name,
                 status: str = "running",
                 cpu_shares: int = None,
                 memory: str = None,
                 vnc_address: str = None
                 ):
        if uuid is None:
            uuid = self._gen_uuid()
        self.uuid = uuid
        self.name = name
        self.container_id = container_id
        self.user_uuid = user_uuid
        self.slave_name = slave_name
        self.status = status
        self.cpu_shares = cpu_shares
        # self.max_cpu = max_cpu
        self.memory_limit = memory
        # self.max_memory = max_memory
        self.vnc_address= vnc_address

    
Base.metadata.create_all(enginefacade.get_engine())
    
    
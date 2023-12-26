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

from __future__ import annotations

from oslo_db.sqlalchemy import enginefacade
from oslo_log import log as logging

from src.Utils.singleton import singleton

LOG = logging.getLogger(__name__)


@singleton
@enginefacade.transaction_context_provider
class DBContext(object):

    def get_session(self):
        return enginefacade.get_legacy_facade().get_session()

    def get_engine(self):
        return enginefacade.get_legacy_facade().get_engine()

from src.utils.sqlalchemy import enginefacade
from src.utils.sqlalchemy.api import *
from .models import Volume, Snapshot

@enginefacade.auto_session
def list_volumes(session, pool_uuid: str):
    if pool_uuid is None:
        return condition_select(session, Volume)
    else:
        return condition_select(session,
                                Volume,
                                values={'pool_uuid': pool_uuid})


@enginefacade.auto_session
def select_volume_by_name(session, pool_uuid: str, name: str):
    volumes = condition_select(session,
                               Volume,
                               values={'pool_uuid': pool_uuid,
                                       'name': name})
    return volumes[0] if len(volumes) > 0 else None


@enginefacade.auto_session
def select_snap_by_volume_uuid(session, volume_uuid: str):
    return condition_select(session,
                            Snapshot,
                            values={'volume_uuid': volume_uuid})
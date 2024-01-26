from src.utils.sqlalchemy import enginefacade
from src.utils.sqlalchemy.api import *
from .models import Volume, Snapshot


@enginefacade.auto_session
def select_volumes(session, **kwargs):
    return condition_select(session,
                            Volume,
                            values=kwargs)


@enginefacade.auto_session
def delete_volume_with_snapshots(session, volume_uuid):
    volume: Volume = select_by_uuid(session, Volume, volume_uuid)
    if volume is None:
        return
    volume.snapshots.clear()
    delete(session, volume)


@enginefacade.auto_session
def select_snapshots(session, **kwargs):
    return condition_select(session,
                            Snapshot,
                            values=kwargs)
from sqlalchemy.orm import Session
from sqlalchemy import select, func


MAINTAINER_LOCK_ID = 10000


def maintainer_lock(session: Session):
    session.execute(select([func.pg_try_advisory_xact_lock(MAINTAINER_LOCK_ID)]))

from typing import Generator
from metadata.core.database import connection

def session_factory() -> Generator:
    yield connection.get_db_session

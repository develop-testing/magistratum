import sqlalchemy as sa

from backend.database.database import metadata, engine

from backend.auth.member.member import make_candidate
from backend.auth.member.sqlalchemy_member import save_candidate

from backend.file_manager.groups.groups import mk_group
from backend.file_manager.groups.sqlalchemy_group import save_group

import backend.file_manager.files.sqlalchemy_file
import backend.file_manager.directories.sqlalchemy_dir
import backend.file_manager.permissions.sqlalchemy_permissions

if __name__ == "__main__":
    with engine.connect() as conn:
        conn.execute(sa.text("DROP TABLE IF EXISTS permissions"))
        conn.commit()

    metadata.drop_all(engine)
    metadata.create_all(engine)

    conn = engine.connect()
    try:
        candidate = make_candidate("root", "root")
        root = save_candidate(conn, candidate)

        rgroup = mk_group("root", root.username, [])
        save_group(conn, rgroup)

        conn.commit()
    finally:
        conn.rollback()
        conn.close()

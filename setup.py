import sqlalchemy as sa

from backend.database.database import metadata, engine

from backend.auth.member.member import make_candidate
from backend.auth.member.sqlalchemy_member import save_candidate

from backend.file_manager.groups.groups import mk_group
from backend.file_manager.groups.sqlalchemy_group import save_group

import backend.file_manager.node.sqlalchemy_node
import backend.image.sqlalchemy_image

if __name__ == "__main__":
    with engine.connect() as conn:
        for tbl in [
            "dirs_to_image",
            "directories",
            "files_to_image",
            "files",
            "dir_permissions",
            "file_permissions",
            "permissions",
            "nodes_to_dir_images",
            "nodes_to_images",
        ]:
            conn.execute(sa.text(f"DROP TABLE IF EXISTS {tbl}"))
        conn.commit()

    metadata.drop_all(engine)
    metadata.create_all(engine)

    conn = engine.connect()
    try:
        candidate = make_candidate("root", "root")
        conn = save_candidate(conn, candidate)

        rgroup = mk_group("root", candidate.username, [])
        conn = save_group(conn, rgroup)

        conn.commit()
    finally:
        conn.rollback()
        conn.close()

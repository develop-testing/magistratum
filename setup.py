import sqlalchemy as sa
from database.database import metadata, engine

from auth.member import make_candidate
from auth.sqlalchemy_member import save_candidate

from files.directory import mk_directory
from files.sqlalchemy_dir import save_directory

from files.permissions.permissions import new_permissions

sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(255), nullable=False, unique=True),
    sa.Column("password", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "files",
    metadata,
    sa.Column("file_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("content", sa.Text, nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "directories",
    metadata,
    sa.Column("dir_id", sa.String(255), nullable=False, unique=True, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False),
    sa.Column("parent_id", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "files_to_dirs",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("file_id", sa.String(255), nullable=False),
    sa.Column("dir_id", sa.Text, nullable=False, unique=False),
)

sa.Table(
    "permissions",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("item_id", sa.String(255), nullable=False),
    sa.Column("owner_id", sa.String(255), nullable=False),
    sa.Column("group_name", sa.String(255), nullable=False),
    sa.Column("content", sa.String(4), nullable=False),
)

if __name__ == "__main__":
    metadata.drop_all(engine)
    metadata.create_all(engine)

    super_admin = make_candidate("root", "root").unwrap()
    member = save_candidate(super_admin).unwrap()

    root_dir = mk_directory("root", member.username).unwrap()
    # permissions = new_permissions(root_dir.dir_id, member.username).unwrap()

    save_directory(root_dir)
    # save_permitions(root_dir)

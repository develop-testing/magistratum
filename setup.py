import sqlalchemy as sa
from database.database import metadata, engine

from auth.member import make_candidate
from auth.sources.sqlalchemy_member import save_candidate

from files.directory import mk_directory
from files.sources.sqlalchemy_dir import save_directory

from files.permissions import new_permissions
from files.sources.sqlalchemy_permissions import save_permissions

from files.groups import mk_group
from files.sources.sqlalchemy_group import save_group

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
    sa.Column("owner_name", sa.String(255), nullable=False),
    sa.Column("group_name", sa.String(255), nullable=False),
    sa.Column("content", sa.String(4), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "groups",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("name", sa.String(255), nullable=False, unique=True),
    sa.Column("owner_name", sa.String(255), nullable=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

sa.Table(
    "users_to_groups",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("user_id", sa.String(255), nullable=False),
    sa.Column("group_id", sa.String(255), nullable=False),
)

if __name__ == "__main__":
    metadata.drop_all(engine)
    metadata.create_all(engine)

    candidate = make_candidate("root", "root").unwrap()
    root = save_candidate(candidate).unwrap()

    rgroup = mk_group("root", root.username, []).unwrap()
    rgroup = save_group(rgroup)

    rhome = mk_directory("root", root.username).unwrap()
    prmns = new_permissions(rhome.dir_id, root.username, "root", "r-r-").unwrap()

    save_directory(rhome)
    save_permissions(prmns)

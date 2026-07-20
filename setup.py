from backend.database.database import metadata, engine

from backend.auth.member import make_candidate
from backend.auth.shell.sources.sqlalchemy_member import save_candidate

from backend.file_manager.directories.directory import new_directory
from backend.file_manager.shell.sources.sqlalchemy_dir import save_directory

from backend.file_manager.directories.home_directory import mk_directory as mk_home_dir
from backend.file_manager.shell.sources.sqlalchemy_home_dir import save_home_dir

from backend.file_manager.permissions import new_permissions
from backend.file_manager.shell.sources.sqlalchemy_permissions import save_permissions

from backend.file_manager.groups import mk_group
from backend.file_manager.shell.sources.sqlalchemy_group import save_group

import backend.file_manager.shell.sources.sqlalchemy_file

if __name__ == "__main__":
    metadata.drop_all(engine)
    metadata.create_all(engine)

    candidate = make_candidate("root", "root")
    root = save_candidate(candidate)

    rgroup = mk_group("root", root.username, [])
    rgroup = save_group(rgroup)

    rhome = new_directory("root", "")
    prmns = new_permissions(rhome.dir_id, root.username, "root", "r-r-")

    save_directory(rhome)
    save_permissions(prmns)

    home = mk_home_dir("root", rhome.dir_id, root.username)
    save_home_dir(home)

from database.database import metadata, engine

from auth.member import make_candidate
from auth.shell.sources.sqlalchemy_member import save_candidate

from file_manager.directories.directory import mk_directory as mk_dir
from file_manager.shell.sources.sqlalchemy_dir import save_directory

from file_manager.directories.home_directory import mk_directory as mk_home_dir
from file_manager.shell.sources.sqlalchemy_home_dir import save_home_dir

from file_manager.permissions import new_permissions
from file_manager.shell.sources.sqlalchemy_permissions import save_permissions

from file_manager.groups import mk_group
from file_manager.shell.sources.sqlalchemy_group import save_group

import file_manager.shell.sources.sqlalchemy_file

if __name__ == "__main__":
    metadata.drop_all(engine)
    metadata.create_all(engine)

    candidate = make_candidate("root", "root").unwrap()
    root = save_candidate(candidate).unwrap()

    rgroup = mk_group("root", root.username, []).unwrap()
    rgroup = save_group(rgroup)

    rhome = mk_dir("root", "").unwrap()
    prmns = new_permissions(rhome.dir_id, root.username, "root", "r-r-").unwrap()

    save_directory(rhome)
    save_permissions(prmns)

    home = mk_home_dir("root", rhome.dir_id, root.username).unwrap()
    save_home_dir(home)

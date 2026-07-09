from database.database import metadata, engine

from auth.member import make_candidate
from auth.sources.sqlalchemy_member import save_candidate

from file_manager.directories.directory import mk_directory
from file_manager.sources.sqlalchemy_dir import save_directory

from file_manager.permissions import new_permissions
from file_manager.sources.sqlalchemy_permissions import save_permissions

from file_manager.groups import mk_group
from file_manager.sources.sqlalchemy_group import save_group

import file_manager.sources.sqlalchemy_file

if __name__ == "__main__":
    metadata.drop_all(engine)
    metadata.create_all(engine)

    candidate = make_candidate("root", "root").unwrap()
    root = save_candidate(candidate).unwrap()

    rgroup = mk_group("root", root.username, []).unwrap()
    rgroup = save_group(rgroup)

    rhome = mk_directory("root", "").unwrap()
    prmns = new_permissions(rhome.dir_id, root.username, "root", "r-r-").unwrap()

    save_directory(rhome)
    save_permissions(prmns)

from dataclasses import dataclass
import sqlalchemy as sa
from result import Ok, Err, Result

from database.database import engine

from .groups import Group, mk_group

import sqlalchemy as sa

def save_group(grp: Group) -> Group:
    create_query = sa.text("""
        INSERT INTO groups (name, owner_name) 
        VALUES (:name, :owner_name)
        RETURNING id
    """)
    
    members_query = sa.text("""
        INSERT INTO users_to_groups (user_id, group_id) 
        VALUES (:user_id, :group_id)
    """)

    with engine.connect() as conn:
        result = conn.execute(
            create_query, 
            {"name": grp.name, "owner_name": grp.owner}
        )
        
        id = result.scalar()

        members_data = [
            {"user_id": user_id, "group_id": id}
            for user_id in grp.members
        ]

        if members_data:
            conn.execute(members_query, members_data)

        conn.commit()

    return grp

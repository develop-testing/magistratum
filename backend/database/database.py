import os

import sqlalchemy as sa

DATABASE_URL = os.environ["DATABASE_URL"]

metadata = sa.MetaData()

engine = sa.create_engine(DATABASE_URL)

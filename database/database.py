import sqlalchemy as sa

DATABASE_URL = "mysql+pymysql://admin:hdjywee2@db:3306/lorica_db"

metadata = sa.MetaData()

engine = sa.create_engine(DATABASE_URL)

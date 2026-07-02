import sqlalchemy as sa

DATABASE_URL = "mysql+pymysql://admin:hdjywee2@db:3306/lorica_db"

metadata = sa.MetaData()

engine = sa.create_engine(DATABASE_URL)

users_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("username", sa.String(255), nullable=False, unique=True),
    sa.Column("password", sa.String(255), nullable=False, unique=False),
    sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
)

if __name__ == "__main__":
    # metadata.drop_all(engine)
    metadata.create_all(engine)

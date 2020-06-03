import sqlalchemy as db

engine = db.create_engine("mysql://root:mysql@localhost:3306/inventory_db")
metadata = db.MetaData(engine)

test = db.Table(
    "test8",
    metadata,
    db.Column('address', db.String(16), primary_key=True),
    db.Column('name', db.String(255)),
)

metadata.create_all()

#!/bin/python3

"""
    Python module to interact with database.
"""
import sqlalchemy as db


class DataBase:

    def __init__(self, db_url):
        self.engine = db.create_engine(db_url, echo=True)
        self.metadata = db.MetaData(self.engine)

        self.inventory = db.Table(
            'inventory',
            self.metadata,
            db.Column('address', db.String(255), primary_key=True),
            db.Column('name', db.String(255), nullable=False),
            db.Column('device_type', db.String(255), nullable=False),
            db.Column('group', db.String(255), nullable=False),
        )

        self.metadata.create_all()

    def connect(self):
        self.conn = self.engine.connect()
        # if self.conn.closed:
        #    raise OSError("Tried to connect to DB server but connection still closed.")

    def disconnect(self):
        self.conn.close()

    def insert(self, data):
        self.result = self.conn.execute(self.inventory.insert(), data)

    def select_one(self, address):
        stmt = self.inventory.select().where(self.inventory.c.address == address)
        result = self.conn.execute(stmt)
        return result.fetchone()

    def select_all(self):
        stmt = self.inventory.select()
        result = self.conn.execute(stmt)
        return result.fetchall()

    def update(self, address, data):
        stmt = self.inventory.update().where(self.inventory.c.address == address).values(**data)
        self.conn.execute(stmt)

    def delete(self, address):
        stmt = self.inventory.delete().where(self.inventory.c.address == address)
        self.conn.execute(stmt)


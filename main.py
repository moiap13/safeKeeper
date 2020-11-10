#!/usr/bin/env python3

from sqlalchemy import Column, String, BLOB, Integer, create_engine, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from simplecrypt import encrypt, decrypt # SROUCE : https://blog.ruanbekker.com/blog/2018/04/29/encryption-and-decryption-with-simple-crypt-using-python/

# Tutorial :    https://stackoverflow.com/questions/41731096/sqlalchemy-query-one-to-many-relationship-with-sqlite
                #https://www.kite.com/python/answers/how-to-execute-raw-sql-queries-in-sqlalchemy-in-python

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.


_db_uri = "sqlite:////tmp/test.db"
Base = declarative_base()
engine = create_engine(_db_uri, echo=False)
Session = sessionmaker(bind=engine)

class Association(Base):
    __tablename__ = 'association'
    filesType = Column(Integer, ForeignKey('filesType.id'), primary_key=True)
    file = Column(Integer, ForeignKey('files.id'), primary_key=True)
    extra_data = Column(String(50))
    child = relationship("Files")

class FilesType(Base):
    __tablename__ = 'filesType'
    id = Column(Integer, primary_key=True)
    type = Column(String(128), unique=False, nullable=False)
    filesAssociated = relationship('Association')

    def __repr__(self):
        _repr_ =("<IndexObject (name='%s')>" % (self.name))
        return _repr_

class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True)
    data = Column(BLOB, nullable=False)

    def __repr__(self):
        __repr__ = ("<IndexObjectACL (value='%s')>" % (self.value))
        return __repr__

Base.metadata.create_all(engine)

"""
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
"""
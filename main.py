#!/usr/bin/env python3

import os
from sqlalchemy import Column, String, BLOB, Integer, create_engine, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from simplecrypt import encrypt, decrypt # SROUCE : https://blog.ruanbekker.com/blog/2018/04/29/encryption-and-decryption-with-simple-crypt-using-python/
import hashlib
import shell


# Tutorial :    https://stackoverflow.com/questions/41731096/sqlalchemy-query-one-to-many-relationship-with-sqlite
                #https://www.kite.com/python/answers/how-to-execute-raw-sql-queries-in-sqlalchemy-in-python

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

CURRENT_DIRECTORY = (os.path.realpath(__file__)).replace(os.path.basename(__file__), "")
_db_uri = "sqlite:///" + CURRENT_DIRECTORY + "/safekeeper.db"
_base = declarative_base()
_engine = None
_session = None
_password = None

class Settings(_base):
    __tablename__ = "settings"
    firstname = Column(String(128))
    lastname = Column(String(128))
    password = Column(String(64), primary_key=True)

class Association(_base):
    __tablename__ = 'association'
    filesType = Column(Integer, ForeignKey('filesType.id'), primary_key=True)
    file = Column(Integer, ForeignKey('files.id'), primary_key=True)
    extra_data = Column(String(50))
    child = relationship("Files")

class FilesType(_base):
    __tablename__ = 'filesType'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(128), unique=True, nullable=False)
    filesAssociated = relationship('Association')


class Files(_base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    password = Column(String(64), nullable=True)
    data = Column(BLOB, nullable=False)

    def __repr__(self):
        __repr__ = ("File %d : '%s'\n" % (self.id, self.title))
        return __repr__

def getDBFile():
    _choice = input("Do you want to open an existing file (1) or create a new one (2) ? ").strip().lower()
    if _choice == "1":
        _path = input("Path : ")
        if _path == "." or _path == "": _path = "safekeeper.db"
        if os.path.exists(_path):
            global _db_uri
            _db_uri = "sqlite:///" + _path
        else:
            raise Exception("the given path doesn't exist")
    elif _choice != "2":
        raise Exception("You must only type 1 or 2")
    return _choice

def initDbInstance():
    global _engine
    _engine = create_engine(_db_uri, echo=False)
    _session = sessionmaker(bind=_engine)
    return _session()

def load_settings(session):
    s = session.query(Settings).all()

    return s[0]

def askUserInfos():
    print("The database file is created, now I will ask you some information :")
    firstname = input("Pleasse enter your firstname : ").strip()
    lastname = input("Pleasse enter your lastname : ").strip()
    _password = input("Pleasse enter your password : ").strip()
    return (firstname, lastname, hashlib.sha224(bytes(_password, encoding='utf-8')).hexdigest())
"""
f = open(CURRENT_DIRECTORY + "01-processs.pdf", 'rb')
file_content = f.read()
f.close()

file_content_cryp = encrypt("bivio", file_content)

print("pdf crypted")

#hashed_password = hashlib.sha224(bytes("bivio", encoding='utf-8')).hexdigest()
print("password hashed")

adding_file = Files(data=file_content_cryp, title="01-processs.pdf", password="hashed_password")

print(adding_file.id)

session = Session()

#session.add(adding_file)
#session.commit()
print(adding_file.id)
"""
"""pdf = session.query(FilesType).filter(FilesType.type=="pdf")
pdf = pdf.all()[0]
"""
"""
q = session.query(Files).first()
print(q.data)
"""

"""doRelation = Association(filesType=pdf.id, file=q.id, extra_data="")
session.add(doRelation)
session.commit()"""

sql_query = text("""select f.data from files as f
join association as a on a.file = f.id
join filesType as ft on a.filesType=ft.id
where ft.type='pdf'""")

"""
result = session.execute(sql_query)

result_as_list = result.fetchall()
"""
"""
f = open(CURRENT_DIRECTORY + "01-processs-wrote.pdf", 'wb')
f.write(decrypt("bivio", q.data))
f.close()
"""

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    _choice = getDBFile()
    _session = initDbInstance()
    _settings = None
    if _choice == "1":
        _settings = load_settings(_session)
        _password = input("Please enter the password to unlock the database file : ").strip()
        _hashed_password = hashlib.sha224(bytes(_password, encoding='utf-8')).hexdigest()

        """if _hashed_password != _settings.password:
           raise Exception("wrong password")"""
    else:
        _base.metadata.create_all(_engine)
        __user_info = askUserInfos()
        _settings = Settings(firstname=__user_info[0], lastname=__user_info[1], password=__user_info[2])
        _session.add(_settings)
        _session.commit()

    print("Welcome, " + _settings.firstname)
    __shell = shell.shell(_session, _password)
    __shell.loop()
    _session.close()
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

#!/usr/bin/env python3

import os
from sqlalchemy import Column, String, BLOB, Integer, create_engine, ForeignKey, text
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from simplecrypt import encrypt, decrypt # SROUCE : https://blog.ruanbekker.com/blog/2018/04/29/encryption-and-decryption-with-simple-crypt-using-python/
import hashlib


# Tutorial :    https://stackoverflow.com/questions/41731096/sqlalchemy-query-one-to-many-relationship-with-sqlite
                #https://www.kite.com/python/answers/how-to-execute-raw-sql-queries-in-sqlalchemy-in-python

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

CURRENT_DIRECTORY = (os.path.realpath(__file__)).replace(os.path.basename(__file__), "")

_db_uri = "sqlite:///"+ CURRENT_DIRECTORY + "/test.db"
Base = declarative_base()
engine = create_engine(_db_uri, echo=False)
Session = sessionmaker(bind=engine)

class Settings(Base):
    __tablename__ = "settings"
    firstname = Column(String(128))
    lastname = Column(String(128))
    password = Column(String(64), primary_key=True)

class Association(Base):
    __tablename__ = 'association'
    filesType = Column(Integer, ForeignKey('filesType.id'), primary_key=True)
    file = Column(Integer, ForeignKey('files.id'), primary_key=True)
    extra_data = Column(String(50))
    child = relationship("Files")

class FilesType(Base):
    __tablename__ = 'filesType'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(128), unique=False, nullable=False)
    filesAssociated = relationship('Association')


class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    password = Column(String(64), nullable=True)
    data = Column(BLOB, nullable=False)

    def __repr__(self):
        __repr__ = ("File %d : '%s'\n" % (self.id, self.title))
        return __repr__

Base.metadata.create_all(engine)

f = open(CURRENT_DIRECTORY + "01-processs.pdf", 'rb')
file_content = f.read()
f.close()

file_content_cryp = encrypt("bivio", file_content)

print("pdf crypted")

hashed_password = hashlib.sha224(bytes("bivio", encoding='utf-8')).hexdigest()
print("password hashed")

adding_file = Files(data=file_content_cryp, title="01-processs.pdf", password=hashed_password)

print(adding_file.id)

session = Session()

#session.add(adding_file)
#session.commit()
print(adding_file.id)

"""pdf = session.query(FilesType).filter(FilesType.type=="pdf")
pdf = pdf.all()[0]
"""

q = session.query(Files).first()
print(q.data)


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

f = open(CURRENT_DIRECTORY + "01-processs-wrote.pdf", 'wb')
f.write(decrypt("bivio", q.data))
f.close()

"""
def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
"""
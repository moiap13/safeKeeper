import os
from sqlalchemy import Column, String, BLOB, Integer, create_engine, ForeignKey, text, MetaData, Table
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

from simplecrypt import encrypt, decrypt # SROUCE : https://blog.ruanbekker.com/blog/2018/04/29/encryption-and-decryption-with-simple-crypt-using-python/
import hashlib

CURRENT_DIRECTORY = (os.path.realpath(__file__)).replace(os.path.basename(__file__), "")
_db_uri = "sqlite:///test.db"
Base = declarative_base()
engine = create_engine(_db_uri, echo=False)
Session = sessionmaker(bind=engine)
session = Session()
meta = MetaData()


"""
class Association(Base):
    __tablename__ = 'association'
    filesType = Column(Integer, ForeignKey('filesType.id'), primary_key=True)
    file = Column(Integer, ForeignKey('files.id'), primary_key=True)
    extra_data = Column(String(50))
    child = relationship("Files")
"""

association = Table(
    'association', meta,
    Column('filesType', Integer, ForeignKey('filesType.id'), primary_key=True),
    Column('file', Integer, ForeignKey('files.id'), primary_key=True),
    Column('extra_data', String(50))
)

"""
class FilesType(Base):
    __tablename__ = 'filesType'
    id = Column(Integer, primary_key=True, autoincrement=True)
    type = Column(String(128), unique=True, nullable=False)
    filesAssociated = relationship('Association')
"""

filesType = Table(
    'filesType', meta,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('type', String(128), unique=True, nullable=False),
) 

"""
class Files(Base):
    __tablename__ = 'files'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    password = Column(String(64), nullable=True)
    data = Column(BLOB, nullable=False)
"""

files = Table(
    'files', meta,
    Column('id', Integer, primary_key = True, autoincrement = True),
    Column('title', String(128), nullable=False),
    Column('password', String(64), nullable=True),
    Column('data', BLOB, nullable=False)
)


f = open(CURRENT_DIRECTORY + "01-processs.pdf", 'rb')
file_content = f.read()
f.close()

file_content_cryp = encrypt("bivio", file_content)

print("[*] pdf crypted")

#hashed_password = hashlib.sha224(bytes("bivio", encoding='utf-8')).hexdigest()
print("[*] password hashed")

meta.create_all(engine)
#Base.metadata.create_all(engine)

#adding_file = Files(data=file_content_cryp, title="01-processs.pdf", password="hashed_password")
adding_file = files.insert().values(data=file_content_cryp, title="01-processs.pdf", password="hashed_password")
conn = engine.connect()
result = conn.execute(adding_file)

lastInsertID = result.inserted_primary_key

#print(adding_file.id)
print("LAST INSERTED ID : " + str(lastInsertID[0]))

"""
session.add(adding_file)
session.commit()
"""

""" Test tuto https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_core_selecting_rows.htm """
"""
s = students.select()
conn = engine.connect()
result = conn.execute(s)

for row in result:
   print (row)
"""
""" END test tuto """

"""
q = session.query(Files)
item = q.first()
"""

q = files.select()
item = conn.execute(q).fetchone()

print(item.title)


#print(adding_file.id)

#pdf = session.query(FilesType).filter(FilesType.type=="pdf")
#pdf = pdf.all()[0]

pdf = filesType.select().where(filesType.c.type == "pdf")
pdf = conn.execute(pdf).fetchone()

data = files.select()
data = conn.execute(data).fetchone()

#q = session.query(Files).first()
#print(data.data)

#doRelation = Association(filesType=pdf.id, file=q.id, extra_data="")
#session.add(doRelation)
#session.commit()


#doRelation = association.insert().values(filesType=pdf.id, file=data.id, extra_data="")
#conn.execute(doRelation)

get_all_pdf_files = text("""select f.title from files as f
join association as a on a.file = f.id
join filesType as ft on a.filesType=ft.id
where ft.type='pdf'""")

#result = session.execute(get_all_pdf_files)
result = conn.execute(get_all_pdf_files)

result_as_list = result.fetchall()

f = open(CURRENT_DIRECTORY + "01-processs-wrote.pdf", 'wb')
f.write(decrypt("bivio", data.data))
f.close()

print("[*] pdf copy rewrote")
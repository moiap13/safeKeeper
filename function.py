import threading

import main
import os
import hashlib
from sqlalchemy import text
import re
from simplecrypt import encrypt, decrypt  # SROUCE : https://blog.ruanbekker.com/blog/2018/04/29/encryption-and-decryption-with-simple-crypt-using-python/
import zipfile
from io import BytesIO


class shell_functions:
    __session = None
    __password = None

    def __init__(self, session, password):
        self.__session = session
        self.__password = password

    def decrypt_file(self, id_file, password):
        file = self.__session.query(main.Files).filter(main.Files.id == id_file).first()
        typeId = self.__session.query(main.Association).filter(main.Association.file == id_file).first()
        type = self.__session.query(main.FilesType).filter(main.FilesType.id == typeId.filesType).first()
        hashed_password = hashlib.sha224(bytes(password, encoding='utf-8')).hexdigest()

        if file is None:
            return -1

        if hashed_password != file.password:
            return -2

        decrypted_folder = main.CURRENT_DIRECTORY + main.DECRYPTED_FOLDER + "/"
        if not os.path.isdir(decrypted_folder):
            os.mkdir(decrypted_folder)

        if type.type == "directory":
            zipdata = BytesIO(decrypt(password, file.data))
            my_zipfile = zipfile.ZipFile(zipdata, mode='r', compression=zipfile.ZIP_DEFLATED)
            my_zipfile.extractall(decrypted_folder)
        else:
            f = open(decrypted_folder + decrypt(self.__password, file.title).decode("utf-8"), 'wb')
            f.write(decrypt(password, file.data))
            f.close()

        return 0

    def list_all_files(self):
        return self.__session.query(main.Files).all()

    def list_files_with_type(self, typeFile):
        sql_query = text("""select f.id, f.title from files as f
                            join association as a on a.file = f.id
                            join filesType as ft on a.filesType=ft.id
                            where ft.type='{typeFile}'""".format(typeFile=typeFile))
        result = self.__session.execute(sql_query)
        return result.fetchall()

    def list_files(self, typeFile=None, search=None, reg=None):
        def print_files(title):
            if title.split(".")[-1] == "directory":
                title = title[:-10] + "/"
            print(str(file.id) + " : " + title)

        files = self.list_files_with_type(typeFile) if typeFile is not None else self.list_all_files() # if typeFile is setted get the files with the given type else all the files
        files = files
        for file in files:
            file_title = decrypt(self.__password, file.title).decode("utf-8")
            if search is not None:
                if search in file_title:
                    threading.Thread(target=print_files(file_title)).start()
            elif reg is not None:
                if re.match("%s" % reg, file_title):
                    threading.Thread(target=print_files(file_title)).start()
            else:
                threading.Thread(target=print_files(file_title)).start()

        return files

    def add_file(self, path, password, typeFile):
        if path[0] == "~":
            if os.name == "posix":
                path = os.path.join(os.path.expanduser('~')) + path[1:]
            elif os.name == "nt":
                path = os.path.join(os.environ['USERPROFILE'] + path[2:])

        if os.path.exists(path):
            if os.path.isdir(path):
                zipdata = BytesIO()
                def zipdir(path, ziph):
                    # ziph is zipfile handle
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            ziph.write(os.path.join(root.split("/")[-1], file))

                zipf = zipfile.ZipFile(zipdata, 'w', zipfile.ZIP_DEFLATED)
                zipdir(path, zipf)
                zipf.close()

                file_content_cryp = encrypt(password, zipdata.getbuffer().tobytes())

                filename = path.split("/")[-1] + ".directory"
                file_extension = "directory"
            else:
                f = open(path, 'rb')
                file_contenent = f.read()
                f.close()

                assert file_contenent is not None
                file_content_cryp = encrypt(password, file_contenent)

                filename, file_extension = os.path.splitext(path)

                filename = filename.split("/")[-1] + file_extension
                file_extension = file_extension.split(".")[-1]
        else:
            return -1

        adding_file = main.Files(data=file_content_cryp, title=encrypt(self.__password, filename),
                                 password=hashlib.sha224(bytes(password, encoding='utf-8')).hexdigest())
        self.__session.add(adding_file)
        self.__session.commit()

        if typeFile is None:
            file_type = self.__session.query(main.FilesType).filter(main.FilesType.type == file_extension).first()
        else:
            file_type = self.__session.query(main.FilesType).filter(main.FilesType.type == typeFile).first()

        if file_type is not None:
            file_type_id = file_type.id
        else:
            add_file_type = main.FilesType(type=file_extension)
            self.__session.add(add_file_type)
            self.__session.commit()
            file_type_id = add_file_type.id

        do_relation = main.Association(filesType=file_type_id, file=adding_file.id, extra_data="")
        self.__session.add(do_relation)
        self.__session.commit()

    def delete_file(self, id):
        obj = self.__session.query(main.Files).filter(main.Files.id == id).first()
        if obj is not None:
            self.__session.delete(obj)
        else:
            return -1
        obj = self.__session.query(main.Association).filter(main.Association.file == id).first()
        if obj is not None:
            self.__session.delete(obj)
        else:
            return -2
        self.__session.commit()
        return 0
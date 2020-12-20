import main
import os
import hashlib
from sqlalchemy import text
import re
from simplecrypt import encrypt, \
    decrypt  # SROUCE : https://blog.ruanbekker.com/blog/2018/04/29/encryption-and-decryption-with-simple-crypt-using-python/


class shell_functions:
    __session = None
    __password = None

    def __init__(self, session, password):
        self.__session = session
        self.__password = password

    def decrypt_file(self, id_file, password):
        file = self.__session.query(main.Files).filter(main.Files.id == id_file).first()
        hashed_password = hashlib.sha224(bytes(password, encoding='utf-8')).hexdigest()

        if hashed_password != file.password:
            return 1

        decrypted_folder = main.CURRENT_DIRECTORY + main.DECRYPTED_FOLDER + "/"
        if not os.path.isdir(decrypted_folder):
            os.mkdir(decrypted_folder)

        f = open(decrypted_folder + str(decrypt(password, file.title)), 'wb')
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

    def list_files(self, typeFile=None):
        files = self.list_files_with_type(typeFile) if typeFile is not None else self.list_all_files()# if typeFile is setted get the files with the given type

        for file in files:
            print(str(file.id) + " : " + file.title)
        return files

    def add_file(self, path, password, typeFile):
        if os.path.exists(path):
            f = open(path, 'rb')
            file_contenent = f.read()
            f.close()
        else:
            return -1

        assert file_contenent is not None

        filename, file_extension = os.path.splitext(path)

        filename = filename.split("/")[-1] + file_extension
        file_extension = file_extension.split(".")[-1]

        file_content_cryp = encrypt(password, file_contenent)

        adding_file = main.Files(data=file_content_cryp, title=str(encrypt(password, filename)),
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

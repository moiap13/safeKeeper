import main
import os
import hashlib
from simplecrypt import encrypt, \
    decrypt  # SROUCE : https://blog.ruanbekker.com/blog/2018/04/29/encryption-and-decryption-with-simple-crypt-using-python/


class shell_functions:
    __session = None
    __password = None

    def __init__(self, session, password):
        self.__session = session
        self.__password = password

    def list_files(self):
        q = self.__session.query(main.Files).all()
        for p in q:
            print(p.title)
        return q

    def add_file(self, path, password, typeFile):
        file_contenent = None

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

        adding_file = main.Files(data=file_content_cryp, title=filename,
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

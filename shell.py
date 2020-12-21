import re
import shlex

class shell:
    __session = None
    __password = None
    __shell_functions = None

    ADD_FILE = regexPattern = re.compile("add file *")

    def __init__(self, session, password):
        """init the shell class"""
        import function
        self.__session = session
        self.__password = password
        self.__shell_functions = function.shell_functions(self.__session, self.__password)


    def __shell_show_help(self):
        print("Usage : ")
        print("\t list files : List the files contenent the database")
        print("\t list types : List the typesfiles content in the database")
        print("\t exit : to quit the shell")

    def loop(self):
        _cmd = ""
        while _cmd != "exit":
            _cmd = input("$ ").strip()

            if "list files" in _cmd:
                lst_command = shlex.split(_cmd)
                try:
                    typeFile = lst_command[lst_command.index("-t") + 1]
                except ValueError:
                    typeFile = None
                try:
                    searchTerm = lst_command[lst_command.index("-s") + 1]
                except ValueError:
                    searchTerm = None
                try:
                    reg = lst_command[lst_command.index("-r") + 1]
                except ValueError:
                    reg = None

                self.__shell_functions.list_files(typeFile=typeFile, search=searchTerm, reg=reg)

            elif "add file" in _cmd:
                lst_command = shlex.split(_cmd)
                if "--help" in lst_command:
                    print("help")
                    continue

                try:
                    file = lst_command[lst_command.index("-f") + 1]
                except ValueError:
                    print("-f needed")
                    continue

                try:
                    pwd = lst_command[lst_command.index("-p") + 1]
                except ValueError:
                    pwd = self.__password

                try:
                    typeFile = lst_command[lst_command.index("-t") + 1]
                except ValueError:
                    typeFile = None

                if self.__shell_functions.add_file(file, pwd, typeFile) != -1:
                    print("File added successfully")
                else:
                    print("The given path doesn't exist")

            elif "decrypt" in _cmd:
                lst_command = shlex.split(_cmd)
                try:
                    id_file = lst_command[lst_command.index("-i") + 1]
                except ValueError:
                    print("-i needed")
                    continue

                try:
                    pwd = lst_command[lst_command.index("-p") + 1]
                except ValueError:
                    pwd = self.__password

                if self.__shell_functions.decrypt_file(id_file, pwd) == 0:
                    print("File decrypted successfully !")
                else:
                    print("The password didn't match")

            elif _cmd == "exit":
                pass
            else:
                self.__shell_show_help()
import re
import shlex

class shell:
    __session = None
    __password = None
    __shell_functions = None

    ADD_FILE = regexPattern = re.compile("add file *")
    ADD_FILE2 = regexPattern = re.compile("add file")

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

    def loop(self):
        _cmd = ""
        while (_cmd != "exit"):
            _cmd = input("$ ").strip()

            if _cmd == "list files":
                """List files here"""
                self.__shell_functions.list_files()
            elif "add file" in _cmd :
                lst_command = shlex.split(_cmd)
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
            elif _cmd == "exit":
                pass
            else:
                self.__shell_show_help()
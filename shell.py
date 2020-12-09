class shell:
    __session = None
    __password = None
    __shell_functions = None

    def __init__(self, session, password):
        """init the shell class"""
        import function
        self.__session = session
        self.__password= password
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
            elif _cmd == "exit":
                pass
            else:
                self.__shell_show_help(self)
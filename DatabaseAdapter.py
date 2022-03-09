import sqlite3


class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class DatabaseAdapter(metaclass=SingletonMeta):
    def __init__(self, database_path):
        self.__db = sqlite3.connect(database_path)

    def insert_user(self, firstname, surname, password, current_layout):
        """

        :param firstname: firstname
        :param surname: surname
        :param password: password
        :param current_layout: Current layout (JSON format)
        :return: None
        """

        sql_query = "INSERT INTO USERS VALUES (null,?,?,?,?)"

        self.__db.execute(sql_query, (firstname, surname, password, current_layout))
        self.__db.commit()

    def get_users(self):
        """
        Returns all users, where each user is a tuple in the form:
        (user_id, firstname, surname)

        :return: list[(int, string, string)]
        """

        sql_query = "SELECT user_id, firstname, surname FROM USERS"

        cursor = self.__db.execute(sql_query)
        return cursor.fetchall()

    def update_user(self, user_id, new_firstname, new_surname, new_password):
        """

        Update a user by his user_id.

        :param user_id: user_id of user to update
        :param new_firstname: new firstname
        :param new_surname: new surname
        :param new_password: new password
        :return: None
        """

        sql_query = "UPDATE Users SET firstname=?, surname=?, password=? WHERE user_id==?"
        self.__db.execute(sql_query, (new_firstname,
                                      new_surname,
                                      new_password,
                                      user_id))
        self.__db.commit()

    def get_layout_of_user(self, user_id):
        """
        Get the current layout of a user. If it doesn´t exist, return None

        :param user_id: user_id
        :return: None
        """

        sql_query = "SELECT current_layout FROM USERS WHERE user_id==?"
        cursor = self.__db.execute(sql_query, user_id)
        layout = cursor.fetchone()

        if layout:
            return layout[0]
        else:
            return None

    def set_layout_of_user(self, user_id, layout):
        """
        Set the current layout of a user

        :param layout: Layout in JSON format
        :param user_id: user_id
        :return: None
        """

        sql_query = "UPDATE Users SET current_layout=? WHERE user_id==?"
        self.__db.execute(sql_query, (layout, user_id))
        self.__db.commit()

    def get_module_configs(self, user_id):
        """
        Return the available modules and their configurations from the DB.
        If a user with has a custom configuration of a module, it is returned, else the default config is returned.

        :param user_id: Id of the user
        :return: A list of module tuples: (module_name, configuration_json)
        """

        sql_query = "SELECT name, ifnull(configuration, default_config) as configuration FROM Modules \
                LEFT OUTER JOIN (SELECT * FROM ModuleConfigurations WHERE user_id=?) as a ON Modules.name = a.module;"
        cursor = self.__db.execute(sql_query, (user_id,))
        return cursor.fetchall()

    def close(self):
        self.__db.close()

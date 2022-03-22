import sqlite3

from util import CONSTANTS


class DatabaseAdapter:
    def __init__(self):
        self.__db = sqlite3.connect(CONSTANTS.DATABASE_PATH)

    def insert_user(self, firstname, lastname, password):
        """

        :param firstname: firstname
        :param lastname: lastname
        :param password: password
        :param current_layout: Current layout (JSON format)
        :return: None
        """

        # insert default layout
        sql_query = "SELECT current_layout FROM USERS WHERE user_id==0"
        cursor = self.__db.execute(sql_query)
        current_layout = cursor.fetchone()[0]

        sql_query = "INSERT INTO USERS VALUES (null,?,?,?,?)"
        self.__db.execute(sql_query, (firstname, lastname, password, current_layout))
        self.__db.commit()

    def get_users(self):
        """
        Returns all users, where each user is a tuple in the form:
        (user_id, firstname, lastname)

        :return: list[(int, string, string)]
        """

        sql_query = "SELECT user_id, firstname, lastname FROM USERS"

        cursor = self.__db.execute(sql_query)
        return cursor.fetchall()

    def update_user(self, user_id, new_firstname, new_lastname):
        """

        Update a user by his user_id.

        :param user_id: user_id of user to update
        :param new_firstname: new firstname
        :param new_lastname: new lastname
        :return: None
        """

        sql_query = "UPDATE Users SET firstname=?, lastname=? WHERE user_id==?"
        self.__db.execute(sql_query, (new_firstname,
                                      new_lastname,
                                      user_id))
        self.__db.commit()

    def delete_user(self, user_id):
        """
        Delete a user.

        :param user_id: user_id
        :return: None
        """

        sql_query = "DELETE FROM ModuleConfigurations WHERE user_id=?"
        self.__db.execute(sql_query, (user_id,))
        sql_query = "DELETE FROM Users WHERE user_id=?"
        self.__db.execute(sql_query, (user_id,))
        self.__db.commit()

    def get_next_user_id(self):
        """
        return the next user_id when a use is created.
        :return:
        """
        sql_query = "SELECT MAX(user_id) FROM Users"
        cursor = self.__db.execute(sql_query)
        return cursor.fetchone()[0] + 1

    def get_layout_of_user(self, user_id):
        """
        Get the current layout of a user. If it doesn't exist, return None

        :param user_id: user_id
        :return: None
        """

        sql_query = "SELECT current_layout FROM USERS WHERE user_id==?"
        cursor = self.__db.execute(sql_query, str(user_id))
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


def main():
    adapter = DatabaseAdapter()
    adapter.get_next_user_id()


if __name__ == "__main__":
    main()

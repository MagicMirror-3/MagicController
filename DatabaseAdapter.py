import json
import sqlite3

from util import CONSTANTS


class DatabaseAdapter:
    def __init__(self):
        self.__db = sqlite3.connect(CONSTANTS.DATABASE_PATH)

    def setup_database(self):

        # create the tables
        configs = 'CREATE TABLE ModuleConfigurations (user_id INTEGER NOT NULL, module TEXT NOT NULL, configuration ' \
                  'TEXT NOT NULL, PRIMARY KEY("user_id", "module")) '
        modules = 'CREATE TABLE Modules (name TEXT NOT NULL UNIQUE, default_config TEXT, PRIMARY KEY(name))'
        users = 'CREATE TABLE "Users" (user_id INTEGER not null primary key autoincrement unique, firstname TEXT not ' \
                'null, lastname TEXT not null, current_layout TEXT not null) '

        self.__db.execute(configs)
        self.__db.execute(modules)
        self.__db.execute(users)
        self.__db.commit()

        # default_layout
        default_layout = [
            {"module": "clock", "position": "top_right",
             "config": {"location": "New York", "appid": "YOUR_OPENWEATHER_API_KEY"}},
            {"module": "compliments", "position": "lower_third", "config": {}},
            {"module": "clock", "position": "bottom_bar", "config": {}}
        ]

        # create default user
        sql_query = "INSERT INTO USERS VALUES (0,?,?,?)"
        self.__db.execute(sql_query, ("default", "default", json.dumps(default_layout)))
        self.__db.commit()

    def insert_user(self, firstname, lastname):
        """

        :param firstname: firstname
        :param lastname: lastname
        :return: None
        """

        # insert default layout
        sql_query = "SELECT current_layout FROM USERS WHERE user_id=0"
        cursor = self.__db.execute(sql_query)
        current_layout = cursor.fetchone()[0]

        sql_query = "INSERT INTO USERS VALUES (null,?,?,?)"
        self.__db.execute(sql_query, (firstname, lastname, current_layout))
        self.__db.commit()

    def get_users(self):
        """
        Returns all users, where each user is a tuple in the form:
        (user_id, firstname, lastname)

        :return: list[(int, string, string)]
        """

        sql_query = "SELECT user_id, firstname, lastname FROM USERS WHERE user_id > 0"

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

        sql_query = "UPDATE Users SET firstname=?, lastname=? WHERE user_id=?"
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
        sql_query = "SELECT seq FROM sqlite_sequence WHERE name = 'Users'"
        cursor = self.__db.execute(sql_query)
        return cursor.fetchone()[0] + 1

    def get_layout_of_user(self, user_id):
        """
        Get the current layout of a user. If it doesn't exist, return None

        :param user_id: user_id
        :return: None
        """

        sql_query = "SELECT current_layout FROM USERS WHERE user_id=?"
        cursor = self.__db.execute(sql_query, (str(user_id),))
        layout = cursor.fetchone()

        if layout:
            return layout[0]
        else:
            return None

    def set_layout_of_user(self, user_id, layout):
        """
        Set the current layout of a user and save the user specific configurations

        :param layout: Layout in JSON format
        :param user_id: user_id
        :return: None
        """

        sql_query = "UPDATE Users SET current_layout=? WHERE user_id=?"
        self.__db.execute(sql_query, (layout, user_id))
        self.__db.commit()

        # update the user specific configurations in the ModuleConfigurations Table
        modules = json.loads(layout)
        for module in modules:
            if module['config'] != {}:
                config = json.dumps(module['config'])
                self.update_module_config(user_id, module['module'], config)

    def update_module_config(self, user_id, module_name, config):
        """
        Update the user specific configuration of a module.

        :param user_id: user_id
        :param module_name: name of the module
        :param config: config JSON of the module
        :return: None
        """

        sql_query = "INSERT INTO ModuleConfigurations VALUES(?,?,?) ON CONFLICT(user_id, module) DO UPDATE SET " \
                    "configuration=? "
        self.__db.execute(sql_query, (user_id, module_name, config, config))
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

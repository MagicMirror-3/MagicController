# examples/things.py

# Let's get this party started!
import json
from wsgiref.simple_server import make_server

import falcon
import sqlite3


class Route:
    def __init__(self, db):
        self.db = db


class CreateUser(Route):
    def on_post(self, req, resp):
        """
        Create a user. Expects Dictionary of following type:

        {
            "firstname": String,
            "surname": String,
            "password": String,
            "current_layout": String,
            "images": [
                image1,
                image2,
                image3, --> all base64 encoded
                ...
            ]
        }

        """
        request_data = req.get_media()

        sql_query = "INSERT INTO USERS VALUES (null, :firstname, :surname, :password, :current_layout)"
        # todo: Call Image recognition
        self.db.execute(sql_query, request_data)
        self.db.commit()

        resp.status = falcon.HTTP_201

        # todo: not created


class GetUsers(Route):
    def on_get(self, req, resp):
        """
        Return firstname, surname and user_id of all users as JSON. This will have to form:

        {
            "user_id": INTEGER
            "firstname": STRING,
            "surname": STRING,
        }

        """

        sql_query = "SELECT user_id, firstname, surname FROM USERS"
        cursor = self.db.execute(sql_query)
        results = cursor.fetchall()
        users = []
        for user_id, firstname, surname in results:
            user = {"user_id": user_id, "firstname": firstname, "surname": surname}
            users.append(user)

        resp.media = users
        resp.status = falcon.HTTP_200


class UpdateUser(Route):
    def on_post(self, req, resp):
        """
        Updates a user by it´s user id. Expects JSON of following type:

        {
            "user_id": INTEGER
            "firstname": String,
            "surname": String,
            "new_password": String,
        }

        """

        request_data = req.get_media()
        sql_query = "UPDATE Users SET firstname=?, surname=?, password=? WHERE user_id==?"
        self.db.execute(sql_query, (request_data['firstname'],
                                    request_data['surname'],
                                    request_data['new_password'],
                                    request_data['user_id']))
        self.db.commit()

        resp.status = falcon.HTTP_201


class GetLayout(Route):
    def on_get(self, req, resp):
        """
        Get the current_layout of a user_id. The JSON returned will look similar to this.
        The parameter "layout" specifies the config file.

        {
            "layout": {
                "modules": [
                    {
                        "module": "clock",
                        "position": "top_left"
                    },
                    {
                        "module": "compliments",
                        "position": "lower_third"
                    },
                    {
                        "module": "currentweather",
                        "position": "top_right",
                        "config": {
                            "location": "New York",
                            "appid": "YOUR_OPENWEATHER_API_KEY"
                        }
                    }
                ]
            }
        }

        """

        params = req.params

        if 'user_id' in params:
            sql_query = "SELECT current_layout FROM USERS WHERE user_id==?"
            cursor = self.db.execute(sql_query, params['user_id'])
            layout = cursor.fetchone()[0]

            resp.media = json.loads(layout)

            resp.status = falcon.HTTP_200
        else:
            resp.status = falcon.HTTP_400


class SetLayout(Route):
    def on_post(self, req, resp):
        """
        Sets the layout of a given user. It expects a JSON with the following structure.

        {
            user_id: INTEGER,
            layout: {*the config*}
        }

        """

        request_data = req.get_media()

        user_id = request_data['user_id']
        layout = json.dumps(request_data['layout'])

        sql_query = "UPDATE Users SET current_layout=? WHERE user_id==?"
        self.db.execute(sql_query, (layout, user_id))
        self.db.commit()

        resp.status = falcon.HTTP_201


class GetModules(Route):
    def on_get(self, req, resp):
        """
        Return the available modules and their configurations on the PI.
        If a user with "user_id" has set a configuration, it is returned, else the default config is returned.
        A JSON String for two modules could look like this:

        [
            {
                "module_name": "uhr",
                "configuration": {
                    "location": "Burgstall",
                    "appid": "KEY",
                    "custom": "yes"
                }
            },
            {
                "module_name": "kalender",
                "configuration": {
                    "calender": "Microsoft",
                    "appid": "KEY",
                    "custom": "yes"
                }
            }
        ]

        """

        user_id = req.params['user_id']

        sql_query = "SELECT name, ifnull(configuration, default_config) as configuration FROM Modules \
        LEFT OUTER JOIN (SELECT * FROM ModuleConfigurations WHERE user_id=?) as a ON Modules.name = a.module;"
        cursor = self.db.execute(sql_query, (user_id,))
        modules = cursor.fetchall()

        modules_list = []
        for module_name, configuration in modules:
            modules_list.append({"module_name": module_name, "configuration": json.loads(configuration)})

        resp.media = modules_list
        resp.status = falcon.HTTP_200


class IsMaggicMirror:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


def main():
    # database connection
    db = sqlite3.connect('MagicMirrorDB.db')

    # Resources are represented by long-lived class instances
    createUser = CreateUser(db)
    getUsers = GetUsers(db)
    updateUser = UpdateUser(db)
    getLayout = GetLayout(db)
    setLayout = SetLayout(db)
    getModules = GetModules(db)
    isMagicMirror = IsMaggicMirror()

    # falcon.App instances are callable WSGI apps
    app = falcon.App()

    # add routes
    app.add_route('/createUser', createUser)
    app.add_route('/getUsers', getUsers)
    app.add_route('/updateUser', updateUser)
    app.add_route('/getLayout', getLayout)
    app.add_route('/setLayout', setLayout)
    app.add_route('/getModules', getModules)
    app.add_route("/isMagicMirror", isMagicMirror)

    with make_server('192.168.2.170', 5000, app) as httpd:
    with make_server('localhost', 5000, app) as httpd:
        print('Serving on port 5000...')

        # Serve until process is killed
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server shutdown.")
        finally:
            db.close()


if __name__ == '__main__':
    main()

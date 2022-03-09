import json
from wsgiref.simple_server import make_server

import falcon
import sqlite3
from DatabaseAdapter import DatabaseAdapter


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
        data = req.get_media()

        # todo: Call Face Authentications

        self.db.insert_user(data["firstname"], data["surname"], data["password"], data["current_layout"])

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

        results = self.db.get_users()

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

        self.db.update_user(request_data['user_id'],
                            request_data['firstname'],
                            request_data['surname'],
                            request_data['new_password'])

        resp.status = falcon.HTTP_201


class GetLayout(Route):
    def on_get(self, req, resp):
        """
        Get the current_layout of a user_id. The JSON returned will look similar to this.
        The parameter "layout" specifies the config file.

        {
            "layout": [
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

        """

        user_id = req.params['user_id']
        layout = self.db.get_layout_of_user(user_id)

        resp.media = json.loads(layout)
        resp.status = falcon.HTTP_200


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

        if isinstance(request_data['layout'], list):
            layout = json.dumps(request_data['layout'])
        elif isinstance(request_data['layout'], str):
            layout = request_data['layout']
        else:
            raise Exception

        self.db.set_layout_of_user(request_data['user_id'], layout)

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

        modules = self.db.get_module_configs(req.params['user_id'])

        # convert the database result into json
        modules_json = []
        for module_name, configuration in modules:
            modules_json.append({"module": module_name, "config": json.loads(configuration)})

        resp.media = modules_json
        resp.status = falcon.HTTP_200


class IsMagicMirror:
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_200


def main():
    # database connection
    db = DatabaseAdapter("../MagicMirrorDB.db")

    # Resources are represented by long-lived class instances
    createUser = CreateUser(db)
    getUsers = GetUsers(db)
    updateUser = UpdateUser(db)
    getLayout = GetLayout(db)
    setLayout = SetLayout(db)
    getModules = GetModules(db)
    isMagicMirror = IsMagicMirror()

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

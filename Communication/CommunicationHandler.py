import json
import threading
from threading import Thread, Event
from wsgiref.simple_server import make_server

import falcon
import requests

from DatabaseAdapter import DatabaseAdapter
from util import get_image_from_base64
from util import get_ip


class Route:
    def __init__(self, db):
        self.db = db


class CommunicationHandler:
    def __init__(self, mediator, host):
        # database connection
        super().__init__()

        if host is not None:
            self.host = host
        else:
            self.host = get_ip()

        self.db = None
        self.app = None
        self.mediator = mediator

        self.thread = Thread(target=self.run, name="CommunicationHandler")
        self.thread.start()

    @staticmethod
    def refresh_layout():
        def request_refresh():
            try:
                requests.request(method="post", url="http://localhost:8080/refresh")
            except requests.exceptions.ConnectionError:
                print("Could not refresh the layout")

        Thread(target=request_refresh).start()

    class CreateUser(Route):
        def __init__(self, db, mediator):
            super().__init__(db)
            # self.face_authentication = FaceAuthentication()
            self.registration_successful = None
            self.mediator = mediator

        def set_registration_successful(self, event, success):
            print("call reg_successful")
            self.registration_successful = success
            event.set()

        def on_post(self, req, resp):
            """
            Create a user. Expects Dictionary of following type:

            {
                "firstname": String,
                "lastname": String,
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
            images = data["images"][1:-1].split(",")
            # with open("images.txt", "w") as f:
            #    f.write(data["images"])
            images = [get_image_from_base64(base64_string) for base64_string in images]

            # get the id, the user will be created with
            user_id = self.db.get_next_user_id()

            # async wait for response
            event = threading.Event()
            callback_function = lambda success: self.set_registration_successful(event, success)

            # notify with callback function
            self.mediator.notify(self, callback_function, user_id, images)
            # wait, until the event is set. This happens, when the
            event.wait()

            # When registration was successful, add the user to the database
            if self.registration_successful:
                # When face_authentication returns true, the user was created.
                resp.status = falcon.HTTP_201
                resp.media = user_id
                self.db.insert_user(data["firstname"], data["lastname"])
            else:
                # When it returns false, the user was not created, because the request did not contain good images
                resp.status = falcon.HTTP_400

    class GetUsers(Route):
        def on_get(self, req, resp):
            """
            Return firstname, lastname and user_id of all users as JSON. This will have to form:

            {
                "user_id": INTEGER
                "firstname": STRING,
                "lastname": STRING,
            }

            """

            results = self.db.get_users()

            users = []
            for user_id, firstname, lastname in results:
                user = {"user_id": user_id, "firstname": firstname, "lastname": lastname}
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
                "lastname": String,
            }

            """

            request_data = req.get_media()

            self.db.update_user(request_data['user_id'],
                                request_data['firstname'],
                                request_data['lastname'])

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

    class DeleteUser(Route):
        def __init__(self, db, mediator):
            super().__init__(db)
            self.mediator = mediator

        def on_post(self, req, resp):
            """
            Delete a user. Expects a JSON string of the following format:

            {
                "user_id": INTEGER
            }

            """
            request_data = req.get_media()
            user_id = request_data['user_id']

            # delete user from database
            self.db.delete_user(user_id)

            # delete user from face_authentication
            self.mediator.notify(self, user_id)

            resp.status = falcon.HTTP_201

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

    def run(self):
        self.db = DatabaseAdapter()

        # Resources are represented by long-lived class instances
        createUser = self.CreateUser(self.db, self.mediator)
        getUsers = self.GetUsers(self.db)
        updateUser = self.UpdateUser(self.db)
        getLayout = self.GetLayout(self.db)
        setLayout = self.SetLayout(self.db)
        deleteUser = self.DeleteUser(self.db, self.mediator)
        getModules = self.GetModules(self.db)
        isMagicMirror = self.IsMagicMirror()

        # falcon.App instances are callable WSGI apps
        self.app = falcon.App()

        # add routes
        self.app.add_route('/createUser', createUser)
        self.app.add_route('/getUsers', getUsers)
        self.app.add_route('/updateUser', updateUser)
        self.app.add_route('/getLayout', getLayout)
        self.app.add_route('/setLayout', setLayout)
        self.app.add_route('/deleteUser', deleteUser)
        self.app.add_route('/getModules', getModules)
        self.app.add_route("/isMagicMirror", isMagicMirror)

        with make_server(self.host, 5000, self.app) as httpd:
            # Serve until process is killed
            try:
                print('Serving on port 5000...')
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("Server shutdown.")
            finally:
                self.db.close()


if __name__ == '__main__':
    CommunicationHandler(None, get_ip())

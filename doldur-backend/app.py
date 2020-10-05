from flask import Flask, request, render_template, Response, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_cors import CORS
from flask_jwt import JWT, jwt_required, current_identity, _jwt_required
import flask
import json
from functools import wraps
from passlib.context import CryptContext

pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=20
)


app = Flask(__name__, static_folder='./build', static_url_path='/')
api = Api(app)
app.secret_key = "83578435843759874359843"

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

users = {
    1 : {"username": "user1", "password":"abcxyz",'schedule':[]},
    2 : {"username": "user2", "password":"abcxyz",'schedule':[]}
}

number_of_users = 2

def authenticate(username,password):
    for i in users.keys():
        if users[i]["username"] == username and pwd_context.verify(password, users[i]["password"]):
            return User(i,username,users[i]["password"])


def identity(payload):
    user_id = payload["identity"],
    return {"username":user_id}
    #return {"username":users[user_id]["username"]}





jwt = JWT(app, authenticate, identity)


cors = CORS(app)

parser = reqparse.RequestParser()

@app.route('/')
def index():
    return app.send_static_file('index.html')


with open("data.json","r") as f:
    semester_courses  = json.load(f)
with open("musts.json","r") as f:
    musts = json.load(f)


def checkuser(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_identity["username"][0] in list(users.keys()):
            return users[current_identity["username"][0]]["schedule"]
        return False
    return wrapper

class HelloWorld(Resource):
    decorators = [checkuser, jwt_required()]
    def get(self):
        return {'hello': current_identity.username}


def checkuser1(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_identity["username"][0] in list(users.keys()):
            return func(*args, **kwargs)
        return abort(401)
    return wrapper

class AddSchedule(Resource):
    decorators = [checkuser1, jwt_required()]
    def get(self):
        parser.add_argument("schedule",type=str)
        args = parser.parse_args()
        schedule = args.get("schedule")
        users[current_identity["username"][0]]["schedule"] = schedule
        return {"message":"Schedule is added"}, 200


class SignUp(Resource):
    def get(self):
        parser.add_argument("username",type=str)
        parser.add_argument("password",type=str)
        args=parser.parse_args()
        username = args.get("username")
        password = args.get("password")

        if  not username or not password:
            return {"message": f'No username or password'}

        #check if there is collision in username
        for i in users.keys():
            if users[i]["username"] == username:
                return {'message': f'User {username} already exists'}

        global number_of_users
        number_of_users+=1
        users[number_of_users] = {"username":username, "password":pwd_context.encrypt(password),"schedule":[]}

        return {'message': f'User {username} was created.'}

class Courses(Resource):
    def get(self):
        return semester_courses

class Courses2(Resource):
    def get(self):
        return semester_courses

class Must(Resource):
    def get(self):
        parser.add_argument("dept",type=str)
        parser.add_argument("sem",type=str)
        args = parser.parse_args()
        dept = args.get("dept")
        sem = request.args.get("sem")
        return musts[dept][sem]
class Must2(Resource):
    def get(self):
        parser.add_argument("dept",type=str)
        parser.add_argument("sem",type=str)
        args = parser.parse_args()
        dept = args.get("dept")
        sem = request.args.get("sem")
        return musts[dept][sem]

class Course(Resource):
    def get(self):
        parser.add_argument("code",type=str)
        args = parser.parse_args()
        code = args.get("code")
        return semester_courses[code]
        
api.add_resource(Courses,'/courses')
api.add_resource(Courses2,'/robotdegilim.xyz/courses')
api.add_resource(Must,'/musts')
api.add_resource(Must2,'/robotdegilim.xyz/musts')
api.add_resource(Course,'/course')
api.add_resource(SignUp, '/signup')
api.add_resource(HelloWorld, '/schedule')
api.add_resource(AddSchedule, '/addschedule')

if __name__ == '__main__':
    app.run(debug=True)
    pass
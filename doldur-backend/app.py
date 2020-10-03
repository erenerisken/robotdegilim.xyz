from flask import Flask, request, render_template, Response, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_cors import CORS
import flask
import json

app = Flask(__name__, static_folder='./build', static_url_path='/')
api = Api(app)



cors = CORS(app)

parser = reqparse.RequestParser()

@app.route('/')
def index():
    return app.send_static_file('index.html')


with open("data.json","r") as f:
    semester_courses  = json.load(f)
with open("musts.json","r") as f:
    musts = json.load(f)

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

if __name__ == '__main__':
    #app.run(debug=True)
    pass
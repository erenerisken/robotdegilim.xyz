from flask import Flask, request, render_template, Response, make_response
from flask_restful import Resource, Api
from flask_restful import reqparse
from flask_cors import CORS
import json
import os
import logging
from logging.handlers import RotatingFileHandler

# Set up logging with rotation
log_file = 'app.log'
max_log_size = 5 * 1024 * 1024  # 5 MB
backup_count = 3

handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logging.basicConfig(handlers=[handler], level=logging.DEBUG)


from lib.constants import *
import lib.scrape
import lib.musts

app = Flask(__name__, static_folder=build_folder, static_url_path='/')
api = Api(app)
cors = CORS(app)

parser = reqparse.RequestParser()

@app.route('/')
def index():
    return app.send_static_file('index.html')
"""
# Load data
try:
    data_path = os.path.join(export_folder, data_out_name)
    with open(data_path, "r", encoding='utf-8') as f:
        semester_courses = json.load(f)
except Exception as e:
    logging.error(f"Error loading semester courses data: {e}", exc_info=True)
    semester_courses = {}
try:
    data_path = os.path.join(export_folder, departments_out_name)
    with open(data_path, "r", encoding='utf-8') as f:
        departments = json.load(f)
except Exception as e:
    logging.error(f"Error loading semester courses data: {e}", exc_info=True)
    departments = {}

try:
    musts_path = os.path.join(export_folder, musts_out_name)
    with open(musts_path, "r", encoding='utf-8') as f:
        musts = json.load(f)
except Exception as e:
    logging.error(f"Error loading musts data: {e}", exc_info=True)
    musts = {}

try:
    last_updated_path = os.path.join(export_folder, last_updated_out_name)
    with open(last_updated_path, "r", encoding='utf-8') as f:
        last_updated_info = json.load(f)
except Exception as e:
    logging.error(f"Error loading lastUpdated data: {e}", exc_info=True)
    last_updated_info = {}
class Courses(Resource):
    def get(self):
        return semester_courses

class Musts(Resource):
    def get(self):
        return musts
    
class LastUpdated(Resource):
    def get(self):
        return last_updated_info

class Must(Resource):
    def get(self):
        parser.add_argument("dept", type=str)
        parser.add_argument("sem", type=str)
        args = parser.parse_args()
        dept = args.get("dept")
        sem = request.args.get("sem")
        try:
            return musts[dept][sem]
        except KeyError:
            logging.error(f"Must data not found for department {dept} and semester {sem}")
            return {"error": "Must data not found"}, 404

class Course(Resource):
    def get(self):
        parser.add_argument("code", type=str)
        args = parser.parse_args()
        code = args.get("code")
        try:
            return semester_courses[code]
        except KeyError:
            logging.error(f"Course data not found for code {code}")
            return {"error": "Course data not found"}, 404


class RunMusts(Resource):
    def get(self):
        try:
            lib.musts.run_musts()
            return {"status": "Musts fetching completed successfully"}, 200
        except Exception as e:
            logging.error(f"Error running musts fetching process: {e}", exc_info=True)
            return {"error": "Error running musts fetching process"}, 500
api.add_resource(Courses, '/courses')
api.add_resource(Musts, '/musts-all')
api.add_resource(LastUpdated, '/lastUpdated')
api.add_resource(Must, '/musts')
api.add_resource(Course, '/course')
api.add_resource(RunMusts, '/run-musts')
"""
class RunScrape(Resource):
    def get(self):
        try:
            if lib.scrape.run_scrape()=="busy":
                return{"status":"System is busy"}
            return {"status": "Scraping completed successfully"}, 200
        except Exception as e:
            logging.error(f"Error running scrape process: {e}", exc_info=True)
            return {"error": "Error running scrape process"}, 500

api.add_resource(RunScrape, '/run-scrape')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

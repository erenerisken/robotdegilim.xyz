from flask import Flask, request, redirect
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
import logging

from ops.constants import *
import ops.scrape
import ops.musts
from ops.helpers import get_email_handler
from ops.exceptions import RecoverException # do not delete this line

# Set up logging
log_file = 'app.log'
logger = logging.getLogger(consts.shared_logger)
logger.setLevel(logging.INFO)
handler = logging.FileHandler(log_file)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# Set up email handler for error messages
email_handler = get_email_handler()
if email_handler:
    logger.addHandler(email_handler)

# Initialize Flask app
app = Flask(__name__, static_folder=consts.build_folder, static_url_path='/')
api = Api(app)
cors = CORS(app)

parser = reqparse.RequestParser()

# musts flag
first_run_musts = False
depts_data_available=False

# Middleware: Redirect to /run-musts if first_run_musts is True
@app.before_request
def check_musts_flag():
    global first_run_musts
    global depts_data_available
    if first_run_musts and request.path == "/run-scrape" and depts_data_available:
        return redirect("/run-musts")

@app.route('/')
def index():
    """Serve the frontend index file."""
    return app.send_static_file('index.html')

class RunScrape(Resource):
    def get(self):
        global depts_data_available
        try:
            if ops.scrape.run_scrape() == "busy":
                return {"status": "System is busy"}, 200
            depts_data_available = True
            return {"status": "Scraping completed successfully"}, 200
        except Exception as e:
            logger.error(str(e))
            return {"error": "Error running scrape process"}, 500

class RunMusts(Resource):
    def get(self):
        global first_run_musts
        global depts_data_available
        try:
            if ops.musts.run_musts() == "busy":
                if not first_run_musts:
                    first_run_musts = True
                    return {"status": "System is busy, request is received"}, 200
                return {"status": "System is busy"}, 200
            first_run_musts=False
            return {"status": "Get musts completed successfully"}, 200
        except Exception as e:
            logger.error(str(e))
            if consts.noDeptsErrMsg in str(e):
                depts_data_available=False
                logger.info("scrape process is prioritized")
            return {"error": "Error running get musts process"}, 500

# Add API resources
api.add_resource(RunScrape, '/run-scrape')
api.add_resource(RunMusts, '/run-musts')

# Start Flask app (comment this in production)
# if __name__ == '__main__':
#     import set_secrets,set_idle
#     set_idle.main()
#     set_secrets.set_secrets()
#     lib.constants.consts.init_envs()
#     app.run(host='0.0.0.0', port=3000)

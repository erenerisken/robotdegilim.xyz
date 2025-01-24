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
backup_count = 2

# Configure logging
handler = RotatingFileHandler(log_file, maxBytes=max_log_size, backupCount=backup_count)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logging.basicConfig(handlers=[handler], level=logging.INFO)  # Adjust logging level for production
logger = logging.getLogger("flask.app")  # Explicit Flask app logger
logger.addHandler(handler)

# Import constants and library modules
from lib.constants import *
import lib.scrape
import lib.musts

# Initialize Flask app
app = Flask(__name__, static_folder=build_folder, static_url_path='/')
api = Api(app)
cors = CORS(app)

parser = reqparse.RequestParser()

@app.route('/')
def index():
    """Serve the frontend index file."""
    return app.send_static_file('index.html')

class RunScrape(Resource):
    def get(self):
        try:
            if lib.scrape.run_scrape() == "busy":
                return {"status": "System is busy"}, 409  # Use HTTP 409 for conflicts
            return {"status": "Scraping completed successfully"}, 200
        except Exception as e:
            logger.error(f"Error running scrape process: {e}", exc_info=True)
            return {"error": "Error running scrape process"}, 500

class RunMusts(Resource):
    def get(self):
        try:
            if lib.musts.run_musts() == "busy":
                return {"status": "System is busy"}, 409  # Use HTTP 409 for conflicts
            return {"status": "Get musts completed successfully"}, 200
        except Exception as e:
            logger.error(f"Error running get musts process: {e}", exc_info=True)
            return {"error": "Error running get musts process"}, 500

# Add API resources
api.add_resource(RunScrape, '/run-scrape')
api.add_resource(RunMusts, '/run-musts')

#if __name__ == '__main__':
#    # Debug should be turned off for production
#    app.run(host='0.0.0.0', port=8080)

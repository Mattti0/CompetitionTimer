import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
from threading import Thread
from werkzeug.utils import secure_filename

from competitor import Competitor
from competition import Competition

#  todo: implement IO control for start button and buzzer
def background_task():
    while(True):
        print("Hello from background task!")
        time.sleep(5)

'''
Flask
'''
ALLOWED_EXTENSIONS = ["csv"]
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(42)
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1000 * 1000
    app.config["UPLOAD_FOLDER"] = "tmp"
    
    competition = Competition()

    if os.path.exists("tmp") == False:
        os.mkdir("tmp")

    io_control = Thread(target=background_task, daemon=True)
    io_control.start()

    @app.route("/")
    def default():
        return competition.get_duration()
    
    @app.route("/start")
    def start_competition():
        if competition.start_competition():
            return ({"status": competition.competition_running, "start_time": competition.start_time})
    
    @app.route("/end")
    def end_competition():
        competition.finish_competition()

        return jsonify({"status": competition.competition_running,
                        "start_time": competition.start_time,
                        "end_time": competition.end_time,
                        "duration": time.strftime('%H:%M:%S', time.gmtime(competition.get_duration()))})
    
    @app.route("/finish/<status>/<bib_number>")
    def competitor_finish(status=None, bib_number=None):
        not_finished_statuses = ["dnf", "dsq", "dns"]
        competitor:Competitor = None
        if status == "finish" and bib_number:
            competitor = competition.competitor_finish(int(bib_number))
        elif status.lower() in not_finished_statuses and bib_number:
            competitor = competition.participant_not_finished(int(bib_number), status)
        else:
            return jsonify({"status": "invalid query"})
        
        if competitor:
            return jsonify(competitor.asdict())
        else:
            return jsonify({"status": "invalid query"})

        
    @app.route("/upload_participants", methods=["POST"])
    def upload_participants():
        if "file" not in request.files:
            return jsonify({"success": False})
        
        file = request.files["file"]
        
        if file.filename == "":
            return jsonify({"success": False})
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            full_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(full_path)

            if competition.load_participants(full_path) > 0:
                return jsonify({"success": True, "operation": "upload"})
            else:
                return jsonify({"success": False, "operation": "upload"})

    return app
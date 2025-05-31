from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging

from planner_handling import Planner, Task
from data_handing import retrieve_planner_data, insert_planner_data

import userManagement as dbHandler

# Code snippet for logging a message
# app.logger.critical("message")

app_log = logging.getLogger(__name__)
logging.basicConfig(
    filename="security_log.log",
    encoding="utf-8",
    level=logging.DEBUG,
    format="%(asctime)s %(message)s",
)

# Generate a unique basic 16 key: https://acte.ltd/utils/randomkeygen
app = Flask(__name__)
app.secret_key = b"_53oi3uriq9pifpff;apl"
csrf = CSRFProtect(app)
app.config['WTF_CSRF_ENABLED'] = False

# Redirect index.html to domain root for consistent UX
@app.route("/index", methods=["GET"])
@app.route("/index.htm", methods=["GET"])
@app.route("/index.asp", methods=["GET"])
@app.route("/index.php", methods=["GET"])
@app.route("/index.html", methods=["GET"])
def root():
    return redirect("/", 302)


@app.route("/", methods=["POST", "GET"])
@csp_header(
    {
        # Server Side CSP is consistent with meta CSP in layout.html
        "base-uri": "'self'",
        "default-src": "'self'",
        "style-src": "'self'",
        "script-src": "'self'",
        "img-src": "'self' data:",
        "media-src": "'self'",
        "font-src": "'self'",
        "object-src": "'self'",
        "child-src": "'self'",
        "connect-src": "'self'",
        "worker-src": "'self'",
        "report-uri": "/csp_report",
        "frame-ancestors": "'none'",
        "form-action": "'self'",
        "frame-src": "'none'",
    }
)
def index():
    return render_template("/index.html")

@app.route("/planner.html", methods=["POST", "GET"])
def planner():
    if request.method == "POST":
        # Get planner details
        start_date = request.form.get("start_date")
        num_weeks = request.form.get("num_weeks")

        # Get task details
        title = request.form.get("title")
        description = request.form.get("description")
        due_date = request.form.get("due_date")

        # Print to console so you can check it worked
        print(f"Planner Start Date: {start_date}")
        print(f"Planner Weeks: {num_weeks}")
        print(f"Task Title: {title}")
        print(f"Task Description: {description}")
        print(f"Task Due Date: {due_date}")

        # Save data to the database
        
        # TODO Use temporary ID 1 for testing purposes (change later)
        insert_planner_data(1, start_date, num_weeks)

        # Create a planner with the given start date and number of weeks
        planner_ = Planner(start_date, num_weeks)
        weeks = planner_.create_weeks()

        return render_template("/planner.html", weeks=weeks)

    if request.method == "GET":
        # Retrieve planner data from the database if it exists
        
        # TODO Use temporary ID 1 for testing purposes (change later)
        data = retrieve_planner_data(1)
        if data is not None:
            num_weeks = data[0][1]
            start_date = data[0][2]

            planner_ = Planner(start_date, num_weeks)
            weeks = planner_.create_weeks()

            return render_template("/planner.html", weeks=weeks)

    return render_template("/planner.html", weeks=None)

@app.route("/privacy.html", methods=["GET"])
def privacy():
    return render_template("/privacy.html")


# example CSRF protected form
@app.route("/form.html", methods=["POST", "GET"])
def form():
    if request.method == "POST":
        email = request.form["email"]
        text = request.form["text"]
        return render_template("/form.html")
    else:
        return render_template("/form.html")


# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

from flask import Flask, session
from flask import redirect
from flask import render_template
from flask import request
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging

from planner_handling import render_planner_page
from data_handing import insert_user_data, retrieve_user_data, insert_planner_data, insert_task_data, retrieve_planners

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
    if "user_id" not in session:
        return redirect("/login.html")
    return render_template("/index.html")

@app.route("/signup.html", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Insert the new user into the database
        insert_user_data(username, password)

        return render_template("/signup.html", success=True)

    return render_template("/signup.html")

@app.route("/login.html", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Gets the user id if the user exists and the password is correct
        user_id = retrieve_user_data(username, password)
        if user_id:
            session["user_id"] = user_id
            return render_template("/index.html")

        return render_template("/login.html")

    return render_template("/login.html")

@app.route("/planner.html", methods=["POST", "GET"])
def planner():
    if "user_id" not in session:
        return redirect("/login.html")
    
    user_id = session["user_id"]
    print(user_id)
    
    planner_ids = retrieve_planners()
    chosen_planner = 1  # Default to ID 1, change when user accounts are added

    if request.method == "POST":
        form_type = request.form.get("form_type")
        if form_type == "planner_form":
            chosen_planner = int(request.form.get("selected_planner", 1))
            start_date = request.form.get("start_date")
            num_weeks = request.form.get("num_weeks")
            insert_planner_data(chosen_planner, start_date, num_weeks)
        
        elif form_type == "task_form":
            chosen_planner = int(request.form.get("selected_planner", 1))
            title = request.form.get("title")
            description = request.form.get("description")
            due_date = request.form.get("due_date")
            insert_task_data(chosen_planner, title, description, due_date)
        
        elif form_type == "planner_select":
            chosen_planner = int(request.form.get("chosen_planner"))

        elif form_type == "invite_form":
            invite_id = request.form.get("invite_id")
        
        return render_planner_page(chosen_planner, planner_ids)

    # GET request
    return render_planner_page(chosen_planner, planner_ids)

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

@app.route("/logout.html", methods=["GET"])
def logout():
    session.pop("user_id", None)  # remove user_id from session
    return render_template("/logout.html")

# Endpoint for logging CSP violations
@app.route("/csp_report", methods=["POST"])
@csrf.exempt
def csp_report():
    app.logger.critical(request.data.decode())
    return "done"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)

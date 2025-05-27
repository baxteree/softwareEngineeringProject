from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import jsonify
import requests
from flask_wtf import CSRFProtect
from flask_csp.csp import csp_header
import logging

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
    weeks = []
    sticky_notes = {}  # {week_index: [ {heading, due, note}, ... ]}
    show_form_for = None
    edit_note = None  # (week_idx, note_idx) if editing

    if request.method == "POST":
        option = request.form.get("option")
        number = request.form.get("number")
        try:
            num_weeks = int(number)
            weeks = [f"Week {i+1}" for i in range(num_weeks)]
        except (TypeError, ValueError):
            weeks = []

        # Load existing sticky notes from hidden fields
        for i in range(len(weeks)):
            sticky_notes[i] = []
            note_count = int(request.form.get(f"note_count_{i}", 0))
            for j in range(note_count):
                heading = request.form.get(f"heading_{i}_{j}", "")
                due = request.form.get(f"due_{i}_{j}", "")
                note = request.form.get(f"note_{i}_{j}", "")
                sticky_notes[i].append({"heading": heading, "due": due, "note": note})

        # If user pressed "+" to add a sticky note
        add_note = request.form.get("add_note")
        if add_note is not None:
            show_form_for = int(add_note)

        # If user submitted a new sticky note
        save_note = request.form.get("save_note")
        if save_note is not None:
            week_idx = int(save_note)
            heading = request.form.get("new_heading", "")
            due = request.form.get("new_due", "")
            note = request.form.get("new_note", "")
            sticky_notes[week_idx].append({"heading": heading, "due": due, "note": note})

        # If user pressed "Edit" on a sticky note
        edit_note_val = request.form.get("edit_note")
        if edit_note_val is not None:
            week_idx, note_idx = map(int, edit_note_val.split("_"))
            edit_note = (week_idx, note_idx)

        # If user pressed "Save Edit" on a sticky note
        save_edit_val = request.form.get("save_edit")
        if save_edit_val is not None:
            week_idx, note_idx = map(int, save_edit_val.split("_"))
            heading = request.form.get("edit_heading", "")
            due = request.form.get("edit_due", "")
            note = request.form.get("edit_note_text", "")
            # Defensive: only update if index exists
            if week_idx in sticky_notes and 0 <= note_idx < len(sticky_notes[week_idx]):
                sticky_notes[week_idx][note_idx] = {"heading": heading, "due": due, "note": note}

    return render_template(
        "/planner.html",
        weeks=weeks,
        sticky_notes=sticky_notes,
        show_form_for=show_form_for,
        edit_note=edit_note,
    )

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

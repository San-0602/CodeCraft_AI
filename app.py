# File: app.py
# Project: CodeCraft AI
# Author: S. Sandhya (San-0602)

from pymongo import MongoClient
from datetime import datetime
from flask import Flask, render_template, request, send_file, redirect, url_for, session, flash
from flask_bcrypt import Bcrypt
import cohere
from fpdf import FPDF
import io
from dotenv import load_dotenv
import os

# environment variables
load_dotenv()

# Flask setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Bcrypt
bcrypt = Bcrypt(app)

# MongoDB setup
client = MongoClient(os.getenv("MONGO_URI"))
db = client.codecraft
prompts_collection = db.prompts
users_collection = db.users

# Cohere setup
co = cohere.Client(os.getenv("COHERE_API_KEY"))

generated_code = ""
explanation = ""
pair_prog_history = []
pdf_buffer = None

# Prompts
def build_prompt(ptype, diff, lang, top):
    return f"Generate a {diff.lower()} {ptype.lower()} project in {lang}. Topic: {top}. Include code, project report, and viva questions."

# PDF creation
def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
    buf = io.BytesIO(pdf.output(dest='S').encode('latin-1'))
    return buf

# Splash route
@app.route("/splash")
def splash():
    return render_template("splash.html")

# Home/index
@app.route("/home", methods=["GET", "POST"])
def index():
    global generated_code, explanation, pair_prog_history, pdf_buffer

    form_data = {
        "project_type": "",
        "difficulty": "",
        "language": "",
        "topic": ""
    }

    if request.method == "POST":
        form_data["project_type"] = request.form.get("project_type", "")
        form_data["difficulty"] = request.form.get("difficulty", "")
        form_data["language"] = request.form.get("language", "")
        form_data["topic"] = request.form.get("topic", "")
        action = request.form.get("action")
        user_question = request.form.get("user_question")

        prompts_collection.insert_one({
            "project_type": form_data["project_type"],
            "difficulty": form_data["difficulty"],
            "language": form_data["language"],
            "topic": form_data["topic"],
            "timestamp": datetime.now()
        })

        if action == "generate":
            prompt = build_prompt(
                form_data["project_type"],
                form_data["difficulty"],
                form_data["language"],
                form_data["topic"]
            )
            response = co.generate(
                model='command-r-plus',
                prompt=prompt,
                max_tokens=4000,
                temperature=0.8,
            )
            generated_code = response.generations[0].text.strip()
            explanation = ""
            pdf_buffer = create_pdf(generated_code)
            pair_prog_history = []

        elif action == "explain" and generated_code:
            explain_prompt = f"Explain the following {form_data['language']} project code step by step in simple terms:\n\n{generated_code}"
            explanation_response = co.generate(
                model='command-r-plus',
                prompt=explain_prompt,
                max_tokens=1500,
                temperature=0.5,
            )
            explanation = explanation_response.generations[0].text.strip()

        elif action == "ask" and user_question and generated_code:
            pair_prompt = (
                f"You are an expert {form_data['language']} developer helping a user understand and improve their code.\n"
                f"The code is:\n{generated_code}\n\n"
                f"User question/request: {user_question}\n\n"
                f"Answer clearly and helpfully."
            )
            pair_response = co.generate(
                model='command-r-plus',
                prompt=pair_prompt,
                max_tokens=1000,
                temperature=0.7,
            )
            answer = pair_response.generations[0].text.strip()
            pair_prog_history.append((user_question, answer))

    return render_template("index.html",
        code=generated_code,
        explanation=explanation,
        history=pair_prog_history,
        form_data=form_data
    )

@app.route("/")
def redirect_to_splash():
    return redirect(url_for("splash"))

# Admin Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "admin" and password == "admin123":
            session["logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials.")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

@app.route("/admin")
def admin_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    prompts = list(prompts_collection.find().sort("timestamp", -1))
    return render_template("admin.html", prompts=prompts)

# User Registration
@app.route("/user-register", methods=["GET", "POST"])
def user_register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        existing_user = db.users.find_one({"username": username})

        if existing_user:
            flash("Username already exists.")
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            db.users.insert_one({
                "username": username,
                "password": hashed_password,
                "joined_on": datetime.now()
            })
            flash("Registration successful! Please log in.")
            return redirect(url_for("user_login"))

    return render_template("user_register.html")

# User Login
@app.route("/user-login", methods=["GET", "POST"])
def user_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = db.users.find_one({"username": username})
        if user and bcrypt.check_password_hash(user["password"], password):
            session["user_logged_in"] = True
            session["user_name"] = username
            flash("Welcome back, " + username + "!")
            return redirect(url_for("index"))
        else:
            flash("Invalid credentials.")
    return render_template("user_login.html")

    code_positions = [{"top": (i * 15) % 100, "left": (i * 17) % 100} for i in range(50)]

    return render_template("user_login.html", code_positions=code_positions)

@app.route("/user-logout")
def user_logout():
    session.pop("user_logged_in", None)
    session.pop("user_name", None)
    flash("You’ve been logged out.")
    return redirect(url_for("index"))

# PDF Download
@app.route("/download")
def download():
    global pdf_buffer
    if pdf_buffer:
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="CodeCraft_Project.pdf")
    return redirect(url_for("index"))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)

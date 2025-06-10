# File: app.py
# Project: CodeCraft AI 
# Author: S. Sandhya (San-0602)

from flask import Flask, render_template, request, send_file, redirect, url_for
import cohere
from fpdf import FPDF
import io
import os

app = Flask(__name__)

co = cohere.Client(API_KEY)

generated_code = ""
explanation = ""
pair_prog_history = []
pdf_buffer = None

def build_prompt(ptype, diff, lang, top):
    return f"Generate a {diff.lower()} {ptype.lower()} project in {lang}. Topic: {top}. Include code, project report, and viva questions."

def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
    buf = io.BytesIO(pdf.output(dest='S').encode('latin-1'))
    return buf

@app.route("/", methods=["GET", "POST"])
@app.route("/", methods=["GET", "POST"])
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

        if action == "generate":
            prompt = build_prompt(form_data["project_type"], form_data["difficulty"], form_data["language"], form_data["topic"])
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

    return render_template(
        "index.html",
        code=generated_code,
        explanation=explanation,
        history=pair_prog_history,
        form_data=form_data  # ✅ Always send this
    )

@app.route("/download")
def download():
    global pdf_buffer
    if pdf_buffer:
        pdf_buffer.seek(0)
        return send_file(pdf_buffer, as_attachment=True, download_name="CodeCraft_Project.pdf")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)

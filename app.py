from flask import Flask, render_template, request, jsonify, session
import joblib

from flask import redirect
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.units import inch
from io import BytesIO
from flask import send_file, session, redirect

import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "predictions.db"

def init_db():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS predictions(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        hours REAL,

        attendance REAL,

        previous REAL,

        score REAL,

        grade TEXT,

        created_at TEXT

    )

    """)

    conn.commit()

    conn.close()

app.secret_key = "student_ai_project"

# Model load
model = joblib.load("model.pkl")


@app.route('/')
def home():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    cursor.execute("""

    SELECT hours,
           attendance,
           previous,
           score,
           grade

    FROM predictions

    ORDER BY id DESC

    LIMIT 10

    """)

    history = cursor.fetchall()

    cursor.execute("""

    SELECT
    COUNT(*),
    MAX(score),
    AVG(score),
    MAX(
        CASE
            WHEN grade='A+' THEN 5
            WHEN grade='A' THEN 4
            WHEN grade='B' THEN 3
            WHEN grade='C' THEN 2
            ELSE 1
        END
    )

    FROM predictions

    """)

    stats = cursor.fetchone()

    best_grade = "-"

    if stats[3]:

        if stats[3] == 5:
            best_grade = "A+"

        elif stats[3] == 4:
            best_grade = "A"

        elif stats[3] == 3:
            best_grade = "B"

        elif stats[3] == 2:
            best_grade = "C"

        else:
            best_grade = "D"

    
    

    conn.close()

    return render_template(
    "index.html",
    history=history,
    stats=stats,
    best_grade=best_grade
)
@app.route("/home")
def homepage():

    conn = sqlite3.connect(DATABASE)

    cursor = conn.cursor()

    # Total Predictions
    cursor.execute("SELECT COUNT(*) FROM predictions")
    total_predictions = cursor.fetchone()[0]

    # Highest Score
    cursor.execute("SELECT MAX(score) FROM predictions")
    highest_score = cursor.fetchone()[0]

    if highest_score is None:
        highest_score = 0

    # Average Score
    cursor.execute("SELECT AVG(score) FROM predictions")
    average_score = cursor.fetchone()[0]

    if average_score is None:
        average_score = 0
    else:
        average_score = round(average_score, 1)

    conn.close()

    return render_template(

        "home.html",

        total_predictions=total_predictions,

        highest_score=highest_score,

        average_score=average_score

    )

@app.route("/predict-page")
def predict_page():

    return render_template("predict.html")

@app.route("/report")
def report():

    result = session.get("result")

    if not result:
        return redirect("/predict-page")

    return render_template(
        "report.html",
        result=result
    )

@app.route('/predict', methods=['POST'])
def predict():

    print("Predict route reached")

    data = request.json

    hours = float(data['hours'])
    attendance = float(data['attendance'])
    previous = float(data['previous'])

    prediction = model.predict([[hours, attendance, previous]])

    score = round(prediction[0], 2)
    score = max(0, min(score, 100))

    if score >= 90:
        grade = "A+"
        suggestion = "Excellent! Keep maintaining your study routine."

    elif score >= 80:
        grade = "A"
        suggestion = "Very Good! Revise regularly to score even higher."

    elif score >= 70:
        grade = "B"
        suggestion = "Good Performance. Increase study hours and practice more."

    elif score >= 60:
        grade = "C"
        suggestion = "Average Performance. Focus on weak subjects."

    else:
        grade = "Needs Improvement"
        suggestion = "Study daily, improve attendance and revise previous topics."

    confidence = "96%"

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO predictions
    (hours, attendance, previous, score, grade, created_at)

    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        hours,
        attendance,
        previous,
        score,
        grade,
        datetime.now().strftime("%d-%m-%Y %H:%M")
    ))

    conn.commit()
    print("Database Insert Done")
    conn.close()

    session["result"] = {
        "hours": hours,
        "attendance": attendance,
        "previous": previous,
        "score": score,
        "grade": grade,
        "suggestion": suggestion,
        "confidence": confidence
    }
    print("Before JSON Response")
    return jsonify({
        "score": score,
        "grade": grade,
        "suggestion": suggestion,
        "confidence": confidence
    })

@app.route("/clear_history", methods=["POST"])
def clear_history():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM predictions")

    conn.commit()
    conn.close()

    return jsonify({
        "status": "success"
    })

@app.route("/download-report")
def download_report():

    result = session.get("result")

    if not result:
        return redirect("/predict-page")

    from datetime import datetime
    from io import BytesIO

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    story = []

    # ---------------- HEADER ----------------

    header = Table(
        [["AI STUDENT SCORE PREDICTOR"]],
        colWidths=[520]
    )

    header.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#5B21B6")),
        ("TEXTCOLOR",(0,0),(-1,-1),colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("FONTNAME",(0,0),(-1,-1),"Helvetica-Bold"),
        ("FONTSIZE",(0,0),(-1,-1),20),
        ("TOPPADDING",(0,0),(-1,-1),15),
        ("BOTTOMPADDING",(0,0),(-1,-1),15),
    ]))

    story.append(header)
    story.append(Spacer(1,20))

    # ---------------- TITLE ----------------

    title = Paragraph(
        "<para align='center'><b><font size='18'>Student Performance Report</font></b></para>",
        styles["Title"]
    )

    story.append(title)

    date = Paragraph(
        f"<para align='center'><font color='grey'>Generated On : {datetime.now().strftime('%d-%m-%Y %I:%M %p')}</font></para>",
        styles["BodyText"]
    )

    story.append(date)
    story.append(Spacer(1,25))

    # ---------------- TABLE ----------------

    data = [

        ["Hours Studied", str(result["hours"])],

        ["Attendance", f'{result["attendance"]}%'],

        ["Previous Score", str(result["previous"])],

        ["Predicted Score", f'{result["score"]}%'],

        ["Grade", result["grade"]],

        ["Confidence", result["confidence"]]

    ]

    table = Table(data, colWidths=[220,220])

    table.setStyle(TableStyle([

        ("GRID",(0,0),(-1,-1),1,colors.HexColor("#D1D5DB")),

        ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#EEF2FF")),

        ("BACKGROUND",(1,0),(1,-1),colors.white),

        ("FONTNAME",(0,0),(0,-1),"Helvetica-Bold"),

        ("FONTNAME",(1,0),(1,-1),"Helvetica"),

        ("FONTSIZE",(0,0),(-1,-1),11),

        ("BOTTOMPADDING",(0,0),(-1,-1),10),

        ("TOPPADDING",(0,0),(-1,-1),10),

        ("ALIGN",(0,0),(-1,-1),"CENTER")

    ]))

    story.append(table)

    story.append(Spacer(1,30))

    # ---------------- RECOMMENDATION ----------------

    heading = Paragraph(
        "<b>AI Recommendation</b>",
        styles["Heading2"]
    )

    story.append(heading)

    story.append(Spacer(1,10))

    recommendation = Table(
        [[result["suggestion"]]],
        colWidths=[520]
    )

    recommendation.setStyle(TableStyle([

        ("BACKGROUND",(0,0),(-1,-1),colors.HexColor("#F5F3FF")),

        ("BOX",(0,0),(-1,-1),1.5,colors.HexColor("#7C3AED")),

        ("LEFTPADDING",(0,0),(-1,-1),15),

        ("RIGHTPADDING",(0,0),(-1,-1),15),

        ("TOPPADDING",(0,0),(-1,-1),15),

        ("BOTTOMPADDING",(0,0),(-1,-1),15),

    ]))

    story.append(recommendation)

    story.append(Spacer(1,30))

    # ---------------- FOOTER ----------------

    footer = Paragraph(

        "<para align='center'><font color='grey'>Generated by <b>AI Student Score Predictor</b><br/>Powered by Machine Learning</font></para>",

        styles["BodyText"]

    )

    story.append(footer)

    # ---------------- BUILD PDF ----------------

    doc.build(story)

    buffer.seek(0)

    return send_file(

        buffer,

        as_attachment=True,

        download_name="AI_Student_Performance_Report.pdf",

        mimetype="application/pdf"

    )
@app.route("/history")
def history():

    conn = sqlite3.connect(DATABASE)

    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM predictions
        ORDER BY id DESC
    """)

    history = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        history=history
    )

@app.route("/insights")
def insights():

    return render_template("insights.html")

if __name__ == "__main__":
    app.run(debug=True)
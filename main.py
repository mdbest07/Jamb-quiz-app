from flask import Flask, render_template, request, session
import random
import json
import os
from question import questions

app = Flask(__name__)
app.secret_key = "jambquiz2026"

def load_scores():
    if os.path.exists("score.json"):
        with open("score.json", "r") as f:
            return json.load(f)
    return []

def save_scores(data):
    with open("score.json", "w") as f:
        json.dump(data, f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/quiz/<subject>")
def quiz(subject):
    subject_questions = [q for q in questions if q["subject"] == subject]
    random.shuffle(subject_questions)
    session["questions"] = subject_questions
    session["subject"] = subject
    session["index"] = 0
    session["score"] = 0
    session["total"] = len(subject_questions)
    return render_template("quiz.html",
        question=subject_questions[0],
        index=1,
        total=len(subject_questions),
        subject=subject
    )

@app.route("/submit", methods=["POST"])
def submit():
    answer = request.form.get("answer", "")
    questions_list = session.get("questions", [])
    index = session.get("index", 0)
    score = session.get("score", 0)
    current = questions_list[index]
    correct = answer.upper() == current["answer"]
    if correct:
        session["score"] = score + 1
    session["index"] = index + 1
    if index + 1 >= len(questions_list):
        final_score = session["score"]
        total = session["total"]
        subject = session["subject"]
        percentage = round(final_score / total * 100, 1)
        scores = load_scores()
        scores.append({
            "subject": subject,
            "score": final_score,
            "total": total,
            "percentage": percentage
        })
        save_scores(scores)
        return render_template("result.html",
            score=final_score,
            total=total,
            percentage=percentage,
            subject=subject
        )
    next_question = questions_list[index + 1]
    return render_template("quiz.html",
        question=next_question,
        index=index + 2,
        total=session["total"],
        subject=session["subject"],
        correct=correct,
        explanation=current["explanation"],
        correct_answer=current["answer"]
    )

@app.route("/scores")
def scores():
    all_scores = load_scores()
    return render_template("scores.html", scores=all_scores)

if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "portal.db")
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-development-secret")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with get_db() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'student'
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            subject TEXT NOT NULL,
            level TEXT NOT NULL,
            goal TEXT NOT NULL,
            format TEXT NOT NULL,
            duration TEXT NOT NULL,
            skills TEXT NOT NULL,
            description TEXT NOT NULL,
            url TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS preferences (
            user_id INTEGER PRIMARY KEY,
            interests TEXT NOT NULL DEFAULT '',
            level TEXT NOT NULL DEFAULT 'Beginner',
            goal TEXT NOT NULL DEFAULT 'Build projects',
            format TEXT NOT NULL DEFAULT 'Video',
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS saved_courses (
            user_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Saved',
            PRIMARY KEY(user_id, course_id),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY(course_id) REFERENCES courses(id) ON DELETE CASCADE
        );
        """)

        count = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
        if count == 0:
            sample_courses = [
                ("Python for Beginners", "Programming", "Beginner", "Build projects", "Video", "6 weeks", "Python, Logic, Basics", "Learn Python syntax, variables, loops and functions with beginner-friendly exercises.", "https://www.learnpython.org/"),
                ("Web Development Fundamentals", "Programming", "Beginner", "Build projects", "Project", "8 weeks", "HTML, CSS, JavaScript", "Build responsive web pages and learn the foundations of the web.", "https://developer.mozilla.org/en-US/docs/Learn"),
                ("Data Structures & Algorithms", "Programming", "Intermediate", "Prepare for placements", "Text", "10 weeks", "Algorithms, Problem Solving", "Practice common data structures, algorithmic thinking and coding interview problems.", "https://www.geeksforgeeks.org/"),
                ("Machine Learning Foundations", "AI & ML", "Intermediate", "Career growth", "Video", "8 weeks", "Python, ML, Data", "Explore supervised learning, model evaluation and introductory machine learning workflows.", "https://www.kaggle.com/learn"),
                ("Introduction to Artificial Intelligence", "AI & ML", "Beginner", "Learn fundamentals", "Video", "5 weeks", "AI concepts, Search, Logic", "Understand AI concepts, search strategies and practical applications.", "https://www.kaggle.com/learn"),
                ("Data Analysis with Python", "Data Science", "Intermediate", "Career growth", "Project", "7 weeks", "Pandas, Data, Charts", "Work with data tables, clean datasets and create useful visualizations.", "https://www.kaggle.com/learn"),
                ("SQL and Database Basics", "Data Science", "Beginner", "Learn fundamentals", "Text", "4 weeks", "SQL, Queries, Tables", "Learn relational database concepts and write SQL queries.", "https://www.w3schools.com/sql/"),
                ("UI/UX Design Essentials", "Design", "Beginner", "Build projects", "Project", "4 weeks", "Wireframes, UX, Design", "Learn user-centered design, wireframes and prototyping fundamentals.", "https://www.figma.com/resource-library/"),
                ("Java Programming", "Programming", "Beginner", "Prepare for placements", "Text", "6 weeks", "Java, OOP, Coding", "Learn Java basics and object-oriented programming principles.", "https://dev.java/learn/"),
                ("Deep Learning Basics", "AI & ML", "Advanced", "Career growth", "Video", "9 weeks", "Neural Networks, Python", "An introduction to neural networks and deep learning workflows.", "https://www.tensorflow.org/learn"),
                ("Statistics for Data Science", "Data Science", "Beginner", "Learn fundamentals", "Video", "5 weeks", "Statistics, Probability", "Build a foundation in probability, distributions and descriptive statistics.", "https://www.khanacademy.org/math/statistics-probability"),
                ("Frontend Portfolio Project", "Programming", "Intermediate", "Build projects", "Project", "3 weeks", "HTML, CSS, JavaScript", "Create and publish a small portfolio project to demonstrate your frontend skills.", "https://developer.mozilla.org/en-US/docs/Learn")
            ]
            db.executemany("""INSERT INTO courses
                (title, subject, level, goal, format, duration, skills, description, url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", sample_courses)


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in to access that page.", "info")
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def score_course(course, interests, level, goal, fmt):
    score = 0
    reasons = []
    if course["subject"] in interests:
        score += 50
        reasons.append("matches your subject")
    if course["level"] == level:
        score += 25
        reasons.append("matches your level")
    if course["goal"] == goal:
        score += 15
        reasons.append("matches your goal")
    if course["format"] == fmt:
        score += 10
        reasons.append("matches your format")
    return score, reasons


@app.route("/")
def index():
    with get_db() as db:
        courses = db.execute("SELECT * FROM courses ORDER BY title LIMIT 6").fetchall()
    return render_template("index.html", courses=courses)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or len(password) < 8:
            flash("Enter your name and email, and use a password of at least 8 characters.", "error")
            return render_template("register.html")
        try:
            with get_db() as db:
                cur = db.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, generate_password_hash(password))
                )
                db.execute("INSERT INTO preferences (user_id) VALUES (?)", (cur.lastrowid,))
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        with get_db() as db:
            user = db.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if user and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    with get_db() as db:
        pref = db.execute("SELECT * FROM preferences WHERE user_id = ?", (session["user_id"],)).fetchone()
        saved = db.execute("""SELECT c.*, s.status FROM saved_courses s
            JOIN courses c ON c.id = s.course_id WHERE s.user_id = ? ORDER BY c.title""",
            (session["user_id"],)).fetchall()
        total = db.execute("SELECT COUNT(*) FROM courses").fetchone()[0]
    return render_template("dashboard.html", pref=pref, saved=saved, total=total)


@app.route("/preferences", methods=["GET", "POST"])
@login_required
def preferences():
    subjects = ["Programming", "AI & ML", "Data Science", "Design"]
    if request.method == "POST":
        interests = [s for s in request.form.getlist("interests") if s in subjects]
        level = request.form.get("level", "Beginner")
        goal = request.form.get("goal", "Build projects")
        fmt = request.form.get("format", "Video")
        if level not in ["Beginner", "Intermediate", "Advanced"]:
            level = "Beginner"
        if goal not in ["Build projects", "Prepare for placements", "Learn fundamentals", "Career growth"]:
            goal = "Build projects"
        if fmt not in ["Video", "Text", "Project"]:
            fmt = "Video"
        with get_db() as db:
            db.execute("""INSERT INTO preferences (user_id, interests, level, goal, format)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET interests=excluded.interests,
                level=excluded.level, goal=excluded.goal, format=excluded.format""",
                (session["user_id"], ",".join(interests), level, goal, fmt))
        flash("Your preferences have been saved.", "success")
        return redirect(url_for("recommendations"))
    with get_db() as db:
        pref = db.execute("SELECT * FROM preferences WHERE user_id = ?", (session["user_id"],)).fetchone()
    selected = pref["interests"].split(",") if pref and pref["interests"] else []
    return render_template("preferences.html", pref=pref, selected=selected, subjects=subjects)


@app.route("/recommendations")
@login_required
def recommendations():
    with get_db() as db:
        pref = db.execute("SELECT * FROM preferences WHERE user_id = ?", (session["user_id"],)).fetchone()
        courses = db.execute("SELECT * FROM courses").fetchall()
    interests = [s for s in (pref["interests"] if pref else "").split(",") if s]
    level = pref["level"] if pref else "Beginner"
    goal = pref["goal"] if pref else "Build projects"
    fmt = pref["format"] if pref else "Video"
    ranked = []
    for course in courses:
        score, reasons = score_course(course, interests, level, goal, fmt)
        ranked.append({"course": course, "score": score, "reasons": reasons})
    ranked.sort(key=lambda item: (item["score"], item["course"]["title"]), reverse=True)
    return render_template("recommendations.html", ranked=ranked, interests=interests)


@app.route("/courses")
def course_catalog():
    query = request.args.get("q", "").strip()
    subject = request.args.get("subject", "").strip()
    with get_db() as db:
        sql = "SELECT * FROM courses WHERE 1=1"
        params = []
        if query:
            sql += " AND (title LIKE ? OR skills LIKE ? OR description LIKE ?)"
            params.extend([f"%{query}%"] * 3)
        if subject:
            sql += " AND subject = ?"
            params.append(subject)
        sql += " ORDER BY title"
        courses = db.execute(sql, params).fetchall()
    return render_template("courses.html", courses=courses, query=query, subject=subject)


@app.post("/save/<int:course_id>")
@login_required
def save_course(course_id):
    status = request.form.get("status", "Saved")
    if status not in ["Saved", "In Progress", "Completed"]:
        status = "Saved"
    with get_db() as db:
        exists = db.execute("SELECT id FROM courses WHERE id = ?", (course_id,)).fetchone()
        if not exists:
            flash("Course not found.", "error")
        else:
            db.execute("""INSERT INTO saved_courses (user_id, course_id, status) VALUES (?, ?, ?)
                ON CONFLICT(user_id, course_id) DO UPDATE SET status=excluded.status""",
                (session["user_id"], course_id, status))
            flash("Learning list updated.", "success")
    return redirect(request.referrer or url_for("dashboard"))


@app.post("/admin/courses")
@login_required
def add_course():
    if session.get("role") != "admin":
        flash("Admin access is required to add courses.", "error")
        return redirect(url_for("dashboard"))
    fields = ["title", "subject", "level", "goal", "format", "duration", "skills", "description", "url"]
    values = [request.form.get(field, "").strip() for field in fields]
    if not all(values):
        flash("Please complete every course field.", "error")
        return redirect(url_for("admin"))
    with get_db() as db:
        db.execute("""INSERT INTO courses
            (title, subject, level, goal, format, duration, skills, description, url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""", values)
    flash("Course added.", "success")
    return redirect(url_for("admin"))


@app.route("/admin")
@login_required
def admin():
    if session.get("role") != "admin":
        flash("Admin access is required.", "error")
        return redirect(url_for("dashboard"))
    with get_db() as db:
        courses = db.execute("SELECT * FROM courses ORDER BY title").fetchall()
    return render_template("admin.html", courses=courses)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

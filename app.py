from ai_model import predict_priority
from ai_type_model import predict_emergency_type

from flask import Flask, render_template, request, redirect, session

import mysql.connector
import os

from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__, template_folder=".")


# =========================
# SECRET KEY
# =========================

app.secret_key = "ai_campus_emergency_secret"


# =========================
# DATABASE CONNECTION
# =========================

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Samiksha@123",
        database="ai_campus_emergency"
    )


# =========================
# HOME
# =========================

@app.route("/")
def home():
    return render_template("home.html")


# =========================
# ABOUT
# =========================

@app.route("/about")
def about():
    return render_template("about.html")


# =========================
# FEATURES
# =========================

@app.route("/features")
def features():
    return render_template("features.html")


# =========================
# CONTACT
# =========================

@app.route("/contact", methods=["GET", "POST"])
def contact():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        message = request.form["message"]

        try:

            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO contact_messages
                (name, email, message)
                VALUES (%s, %s, %s)
            """, (name, email, message))

            db.commit()

            cursor.close()
            db.close()

            return "Message Sent Successfully!"

        except mysql.connector.Error as err:

            return f"Database Error: {err}"

    return render_template("contact.html")


# =========================
# REPORT EMERGENCY
# =========================

@app.route("/report", methods=["GET", "POST"])
def report():

    # Login required
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        # =========================
        # GET USER INPUT
        # =========================

        location = request.form["location"]
        description = request.form["description"]

        # =========================
        # AI EMERGENCY TYPE
        # =========================

        predicted_type = predict_emergency_type(description)

        emergency_type = predicted_type

        # =========================
        # AI PRIORITY
        # =========================

        priority = predict_priority(
            emergency_type + " " + description
        )

        # =========================
        # IMAGE UPLOAD
        # =========================

        image = request.files.get("image")
        image_name = None

        if image and image.filename:

            image_name = image.filename

            upload_folder = os.path.join(
                app.root_path,
                "static",
                "uploads"
            )

            os.makedirs(upload_folder, exist_ok=True)

            image.save(
                os.path.join(
                    upload_folder,
                    image_name
                )
            )

        # =========================
        # SAVE REPORT
        # =========================

        try:

            db = get_db_connection()
            cursor = db.cursor()

            cursor.execute("""
                INSERT INTO reports
                (
                    user_id,
                    emergency_type,
                    location,
                    description,
                    image,
                    priority
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                session["user_id"],
                emergency_type,
                location,
                description,
                image_name,
                priority
            ))

            db.commit()

            cursor.close()
            db.close()

            return render_template(
                "report_success.html",
                emergency_type=emergency_type,
                priority=priority,
                location=location,
                description=description
            )

        except mysql.connector.Error as err:

            return f"Database Error: {err}"

    return render_template("report.html")


# =========================
# USER DASHBOARD
# =========================

@app.route("/dashboard")
def user_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "user":
        return redirect("/login")

    return render_template("user_dashboard.html")


# =========================
# MY REPORTS
# =========================

@app.route("/myreports")
def myreports():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "user":
        return redirect("/login")

    try:

        db = get_db_connection()

        cursor = db.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute("""
            SELECT
                id,
                emergency_type,
                location,
                description,
                image,
                priority,
                status
            FROM reports
            WHERE user_id = %s
            ORDER BY id DESC
        """, (session["user_id"],))

        reports = cursor.fetchall()

        cursor.close()
        db.close()

        return render_template(
            "my_reports.html",
            reports=reports
        )

    except mysql.connector.Error as err:

        return f"Database Error: {err}"


# =========================
# ADMIN DASHBOARD
# =========================

@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return redirect("/dashboard")

    try:

        db = get_db_connection()

        cursor = db.cursor(
            dictionary=True,
            buffered=True
        )

        # =========================
        # EMERGENCY REPORTS
        # =========================

        cursor.execute("""
            SELECT
                id,
                emergency_type,
                location,
                description,
                image,
                priority,
                status
            FROM reports
            ORDER BY id DESC
        """)

        reports = cursor.fetchall()

        # =========================
        # HIGH PRIORITY COUNT
        # =========================

        high_priority_count = sum(
            1
            for report in reports
            if report["priority"] == "High"
        )

        # =========================
        # REGISTERED USERS
        # =========================

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                role
            FROM users
            ORDER BY id DESC
        """)

        users = cursor.fetchall()

        # =========================
        # CONTACT MESSAGES
        # =========================

        cursor.execute("""
            SELECT
                id,
                name,
                email,
                message,
                created_at
            FROM contact_messages
            ORDER BY id DESC
        """)

        contact_messages = cursor.fetchall()

        cursor.close()
        db.close()

        # =========================
        # SEND DATA TO TEMPLATE
        # =========================

        return render_template(
            "admin_dashboard.html",
            reports=reports,
            users=users,
            contact_messages=contact_messages,
            high_priority_count=high_priority_count
        )

    except mysql.connector.Error as err:

        return f"Database Error: {err}"


# =========================
# SET REPORT STATUS
# IN PROGRESS
# =========================

@app.route(
    "/status/<int:report_id>/in-progress",
    methods=["POST"]
)
def set_in_progress(report_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return redirect("/dashboard")

    try:

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE reports
            SET status = 'In Progress'
            WHERE id = %s
        """, (report_id,))

        db.commit()

        cursor.close()
        db.close()

        return redirect("/admin")

    except mysql.connector.Error as err:

        return f"Database Error: {err}"


# =========================
# SET REPORT STATUS
# RESOLVED
# =========================

@app.route(
    "/status/<int:report_id>/resolved",
    methods=["POST"]
)
def set_resolved(report_id):

    if "user_id" not in session:
        return redirect("/login")

    if session.get("role") != "admin":
        return redirect("/dashboard")

    try:

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute("""
            UPDATE reports
            SET status = 'Resolved'
            WHERE id = %s
        """, (report_id,))

        db.commit()

        cursor.close()
        db.close()

        return redirect("/admin")

    except mysql.connector.Error as err:

        return f"Database Error: {err}"


# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        try:

            db = get_db_connection()

            cursor = db.cursor(
                dictionary=True,
                buffered=True
            )

            cursor.execute("""
                SELECT
                    id,
                    name,
                    email,
                    password,
                    role
                FROM users
                WHERE email = %s
            """, (email,))

            user = cursor.fetchone()

            cursor.close()
            db.close()

            # =========================
            # PASSWORD CHECK
            # =========================

            if user and check_password_hash(
                user["password"],
                password
            ):

                session["user_id"] = user["id"]
                session["user_name"] = user["name"]
                session["role"] = user["role"]

                # ADMIN
                if user["role"] == "admin":
                    return redirect("/admin")

                # USER
                else:
                    return redirect("/dashboard")

            else:

                return "Invalid Email or Password"

        except mysql.connector.Error as err:

            return f"Database Error: {err}"

    return render_template("login.html")


# =========================
# REGISTER
# =========================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        try:

            db = get_db_connection()

            cursor = db.cursor(
                dictionary=True,
                buffered=True
            )

            # =========================
            # CHECK DUPLICATE EMAIL
            # =========================

            cursor.execute("""
                SELECT id
                FROM users
                WHERE email = %s
            """, (email,))

            existing_user = cursor.fetchone()

            if existing_user:

                cursor.close()
                db.close()

                return "Email already registered. Please use another email."

            # =========================
            # HASH PASSWORD
            # =========================

            hashed_password = generate_password_hash(
                password
            )

            # =========================
            # CREATE USER
            # =========================

            cursor.execute("""
                INSERT INTO users
                (name, email, password, role)
                VALUES (%s, %s, %s, %s)
            """, (
                name,
                email,
                hashed_password,
                "user"
            ))

            db.commit()

            cursor.close()
            db.close()

            return redirect("/login")

        except mysql.connector.Error as err:

            return f"Database Error: {err}"

    return render_template("register.html")


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
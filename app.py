from flask import Flask, render_template, request, redirect, session, jsonify
from flask_mysqldb import MySQL
from flask_bcrypt import Bcrypt
from datetime import timedelta
import random
import smtplib
from email.mime.text import MIMEText
import qrcode
from io import BytesIO
import base64
import pyotp 
from flask import Flask, render_template
import os

# Initialize Flask app
app = Flask(__name__, template_folder=os.path.abspath("templates"))
app.secret_key = os.urandom(24)
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=15)

# Database Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "root"
app.config["MYSQL_DB"] = "student_auth"

mysql = MySQL(app)
with app.app_context():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db_name = cursor.fetchone()
        print(f"Connected to MySQL Database: {db_name}")
    except Exception as e:
        print("Database connection failed:", e)

bcrypt = Bcrypt(app)

# Email Configuration

EMAIL_ADDRESS = "mageshwaranvijayan@gmail.com"
EMAIL_PASSWORD = "pljenmsarszhmoac"
 # Use an App Password

# Home Route (Login/Register Page)
@app.route("/")
def home():
    return render_template("index.html")

# Register Route
@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    email = request.form["email"]
    department = request.form.get("department", "Unknown")  # Default department if empty
    cgpa = request.form.get("cgpa", "0.0")  # Default CGPA if empty
    password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (name, email, department, cgpa, password_hash) VALUES (%s, %s, %s, %s, %s)",
                       (name, email, department, cgpa, password))
        mysql.connection.commit()
        cursor.close()

    return redirect("/")



# Login Route
@app.route("/login", methods=["POST"])
def login():
    email = request.form["email"]
    password = request.form["password"]

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT user_id, name, email, password_hash FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        cursor.close()

    if user and bcrypt.check_password_hash(user[3], password):  
        session.permanent = True
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        print("Session Set:", session)

        return redirect("/otp")  
    
    return "Invalid Credentials", 401

# OTP Verification Page
@app.route("/otp")
def otp_page():
    if "user_id" not in session:
        return redirect("/")
    return render_template("otp_verification.html")

# Generate OTP (Email or QR)
@app.route("/send-otp", methods=["POST"])
def send_otp():
    data = request.get_json()
    method = data.get("method")

    if "user_id" not in session:
        return jsonify({"error": "Session expired. Please log in again."}), 401

    otp = str(random.randint(100000, 999999))  # Generate a 6-digit OTP

    with app.app_context():
        cursor = mysql.connection.cursor()
        # Delete any previous OTPs for this user
        cursor.execute("DELETE FROM otps WHERE user_id = %s", (session["user_id"],))
        # Store new OTP in database
        cursor.execute("INSERT INTO otps (user_id, otp_code) VALUES (%s, %s)", (session["user_id"], otp))
        mysql.connection.commit()

        # Fetch user email
        cursor.execute("SELECT email FROM users WHERE user_id = %s", (session["user_id"],))
        user_email = cursor.fetchone()[0]
        cursor.close()

    if method == "email":
        msg = MIMEText(f"Your OTP is: {otp}")
        msg["Subject"] = "Your OTP Code"
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = user_email

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, user_email, msg.as_string())
            server.quit()
            return jsonify({"success": True, "message": "OTP sent to your email"})
        except Exception as e:
            return jsonify({"error": f"Email sending failed: {e}"})

    elif method == "qr":
        return generate_qr()
    else:
        return jsonify({"error": "Invalid verification method"}), 400


@app.route("/generate-qr", methods=["POST"])
def generate_qr():
    if "user_id" not in session:
        return jsonify({"error": "User not logged in"}), 401

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT otp_secret FROM users WHERE user_id = %s", (session["user_id"],))
        result = cursor.fetchone()

        # If the user already has an OTP secret, use it; otherwise, generate and save a new one
        if result and result[0]:
            otp_secret = result[0]
        else:
            otp_secret = pyotp.random_base32()  # Generate a new secret key
            cursor.execute("UPDATE users SET otp_secret = %s WHERE user_id = %s", (otp_secret, session["user_id"]))
            mysql.connection.commit()

        cursor.close()

    # Generate OTP URI for Google Authenticator
    otp_uri = pyotp.totp.TOTP(otp_secret).provisioning_uri(session["user_name"], issuer_name="MyApp")

    # Generate QR Code
    img = qrcode.make(otp_uri)
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return jsonify({"success": True, "qr_code": qr_base64})





# Verify OTP Route
@app.route("/verify-otp", methods=["POST"])
def verify_otp():
    if "user_id" not in session:
        return jsonify({"error": "Session expired. Please log in again."}), 401

    entered_otp = request.form["otp"]

    with app.app_context():
        cursor = mysql.connection.cursor()

        # 1. Check if the entered OTP matches the latest stored OTP (for email verification)
        cursor.execute("SELECT otp_code FROM otps WHERE user_id = %s ORDER BY id DESC LIMIT 1", (session["user_id"],))
        db_otp = cursor.fetchone()

        # 2. Check if the entered OTP matches the QR-based TOTP (for Google Authenticator)
        cursor.execute("SELECT otp_secret FROM users WHERE user_id = %s", (session["user_id"],))
        user_secret = cursor.fetchone()
        cursor.close()

    if db_otp and entered_otp == db_otp[0]:  # Email OTP check
        return redirect("/dashboard")

    elif user_secret and user_secret[0]:  # Google Authenticator OTP check
        totp = pyotp.TOTP(user_secret[0])
        if totp.verify(entered_otp):
            return redirect("/dashboard")

    return "Invalid OTP. Please try again.", 401


# Dashboard Page
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/login")

    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT user_id, name, email, department, cgpa FROM users WHERE user_id = %s", (session["user_id"],))
        user = cursor.fetchone()
        cursor.close()

    if user:
        return render_template("deshboard.html", user=user)
    else:
        return "User not found", 404


# Logout Route
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# Run Flask App
if __name__ == "__main__":
    app.run(debug=True)
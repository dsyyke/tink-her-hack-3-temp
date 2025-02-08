from flask import Flask, render_template, request, redirect, url_for, session
from supabase import create_client, Client
import os


# Flask App Configuration
app = Flask(__name__)
app.secret_key = "8f7f773334beeb6d4efc05f4651eb5326a5f3c2e596e03e669964629481572f1"

# Supabase Configuration
SUPABASE_URL = "https://iqowvmjvnynqagdguuqw.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlxb3d2bWp2bnlucWFnZGd1dXF3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzkwNDcxNzMsImV4cCI6MjA1NDYyMzE3M30._NdKQTmtetrjjf4vrGXWyBjCCK9OzEovqWXSh-TOCZg"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# -------------------------------------------
# 🚀 Home Route
# -------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")

# -------------------------------------------
# 🚀 About Route
# -------------------------------------------
@app.route("/about")
def about():
    return render_template("about.html")

# -------------------------------------------
# 🚀 Login Route (Dashboard)
# -------------------------------------------
@app.route("/login-dashboard", methods=["GET", "POST"])
def login_dashboard():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Fetch user from Supabase
        response = supabase.table("users").select("username, password, role, approved").eq("username", username).execute()
        user_data = response.data

        if user_data and user_data[0]["password"] == password:
            session["user"] = username
            session["user_type"] = user_data[0]["role"]
            
            # Redirect based on role
            if session["user_type"] == "admin":
                return redirect(url_for("admin_dashboard"))
            elif session["user_type"] == "student":
                if user_data[0]["approved"]:
                    return redirect(url_for("student_dashboard"))
                else:
                    return render_template("login-dashboard.html", error="Your account is pending admin approval.")

        return render_template("login-dashboard.html", error="Incorrect username or password.")
    
    return render_template("login-dashboard.html")

# -------------------------------------------
# 🚀 Registration Route
# -------------------------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirmPassword"]
        
        if password != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        
        # Check if username already exists
        response = supabase.table("users").select("username").eq("username", username).execute()
        if response.data:
            return render_template("register.html", error="Username already exists")
        
        # Insert user into Supabase
        supabase.table("users").insert({
            "username": username,
            "password": password,
            "role": "student",
            "approved": False
        }).execute()
        
        print("✅ Registration Successful: Data stored in Supabase!")
        return redirect(url_for("login_dashboard"))
    
    return render_template("register.html", error=None)

# -------------------------------------------
# 🚀 Admin Dashboard Route
# -------------------------------------------

@app.route("/admin-dashboard")
def admin_dashboard():
    if "user" in session and session["user_type"] == "admin":
        # Fetch all unapproved students
        response = supabase.table("users").select("id, username").eq("approved", False).execute()
        unapproved_students = response.data
        return render_template("admin-dashboard.html", students=unapproved_students)
    return redirect(url_for("login_dashboard"))

# -------------------------------------------
# 🚀 Student Dashboard Route
# -------------------------------------------
@app.route("/student-dashboard")
def student_dashboard():
    if "user" in session and session["user_type"] == "student":
        return render_template("student-dashboard.html")
    return redirect(url_for("login_dashboard"))

# -------------------------------------------
# 🚀 Logout Route
# -------------------------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login_dashboard"))

# -------------------------------------------
# 🚀 Run Flask App
@app.route("/test-supabase")
def test_supabase():
    try:
        response = supabase.table("users").select("*").limit(1).execute()
        if response.data:
            return f"✅ Connected to Supabase! Sample Data: {response.data}"
        else:
            return "✅ Connected to Supabase, but no data found in 'users' table."
    except Exception as e:
        return f"❌ Failed to connect: {str(e)}"

# -------------------------------------------
if __name__ == "__main__":
    app.config.update(
        SESSION_COOKIE_SECURE=True,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
    )
    app.run(debug=True)

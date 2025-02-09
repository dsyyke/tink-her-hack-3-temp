from flask import Flask, render_template, request, redirect, session, url_for
from firebase_admin import credentials, auth
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/admin-dashboard')
def admin_dashboard():
    return render_template('admin-dashboard.html')

@app.route('/student-dashboard')
def student_dashboard():
    return render_template('student-dashboard.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/login-dashboard', methods=['GET', 'POST'])
def login_dashboard():
    if request.method == 'POST':
        user_type = request.form.get('user_type')  # Get user type (admin/student)
        username = request.form.get('username')
        password = request.form.get('password')

        print(f"Received Login Request - UserType: {user_type}, Username: {username}, Password: {password}")

        try:
            # Authenticate user with Firebase
            user = auth.get_user_by_email(username)

            # Check if user is admin or student
            if user_type == "admin":
                if "admin" in user.custom_claims and user.custom_claims["admin"] == True:
                    session['user'] = username
                    session['user_type'] = "admin"
                    return redirect(url_for('admin-dashboard'))
                else:
                    return "You are not an Admin"

            elif user_type == "student":
                session['user'] = username
                session['user_type'] = "student"
                return redirect(url_for('student-dashboard'))

        except Exception as e:
            return f"Login Failed: {str(e)}"

    return render_template('login-dashboard.html')


@app.route('/Register', methods=['GET', 'POST'])
def register():
    return render_template('Register.html')



if __name__ == '__main__':
    app.run(debug=True)

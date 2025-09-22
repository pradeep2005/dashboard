from flask import Flask, render_template, request, redirect, session
from db_connect import get_db_connection  # <-- import here

app = Flask(__name__)
app.secret_key = "your_secret_key"   # needed for sessions

@app.route('/')
def home():
    if "username" in session:
        return render_template("dashboard.html", username=session["username"])
    return redirect('/login')

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO users (username,email,password) VALUES (%s,%s,%s)", 
                    (username, email, password))
        conn.commit()
        conn.close()
        return redirect('/login')   # <-- after register
    return render_template("register.html")


@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cur.fetchone()
        conn.close()

        if user:
            session["username"] = user["username"]
            return redirect('/')
        else:
            return "Invalid email or password"
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect('/login')

@app.route('/profile')
def profile():
    if "username" in session:
        return render_template("profile.html", username=session["username"])
    return redirect(url_for('login'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if "username" in session:
        # Get form data and update in DB
        username = session["username"]
        email = request.form.get("email")
        fullname = request.form.get("fullname")
        password = request.form.get("password")
        # Save/update logic goes here
        return redirect(url_for('profile'))
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)
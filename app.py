from flask import Flask, render_template, request, redirect, url_for, flash, session
from db_connect import get_db_connection  # your DB connection function

app = Flask(__name__)
app.secret_key = "your_secret_key"  # needed for sessions

# ---------------- Home / Dashboard ----------------
@app.route('/')
@app.route('/dashboard')
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session["username"])
    return redirect('/login')

# ---------------- Register ----------------
@app.route('/register', methods=["GET", "POST"])
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
        return redirect('/login')
    return render_template("register.html")

# ---------------- Login ----------------
@app.route('/login', methods=["GET", "POST"])
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

# ---------------- Logout ----------------
@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect('/login')

# ---------------- Profile ----------------
@app.route('/profile')
def profile():
    if "username" in session:
        return render_template("profile.html", username=session["username"])
    return redirect(url_for('login'))

@app.route('/update_profile', methods=['POST'])
def update_profile():
    # Example: update user info
    if "username" in session:
        # get form data
        new_username = request.form.get("username")
        # update session or database here
        session["username"] = new_username
        return redirect(url_for("profile"))
    return redirect(url_for("login"))


# ---------------- Tasks ----------------
@app.route('/tasks', methods=['GET', 'POST'])
def tasks():
    if "username" not in session:
        return redirect(url_for('login'))

    try:
        conn = get_db_connection()
        cur = conn.cursor(dictionary=True)

        # Add new task
        if request.method == "POST":
            task_name = request.form.get("name")
            status = request.form.get("status")
            employee = request.form.get("employee")
            tool = request.form.get("tool")
            priority = request.form.get("priority")
            due_date = request.form.get("due_date")

            cur.execute("""
                INSERT INTO tasks (name, status, employee, tool, priority, due_date, progress)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (task_name, status, employee, tool, priority, due_date, 0))
            conn.commit()
            flash("Task added successfully!", "success")

        # Fetch all tasks
        cur.execute("SELECT * FROM tasks ORDER BY due_date ASC")
        all_tasks = cur.fetchall()
        conn.close()

        return render_template("tasks.html", tasks=all_tasks, username=session["username"])

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "danger")
        return render_template("tasks.html", tasks=[], username=session.get("username"))

# ---------------- Run App ----------------
if __name__ == "__main__":
    app.run(debug=True)

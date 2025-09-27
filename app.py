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
    
# ---------------- Orders Route ----------------


# ---------------- Clear Orders ----------------
@app.route('/orders', methods=['GET', 'POST'])
def orders():
    if "username" not in session:
        return redirect(url_for('login'))

    username = session["username"]

    if 'work_orders' not in session:
        session['work_orders'] = []

    if request.method == "POST":
        order = {
            "customer": request.form.get("customer", ""),
            "status": request.form.get("status", "Pending"),
            "priority": request.form.get("priority", "Medium"),
            "order_date": request.form.get("order_date", ""),
            "work_date": request.form.get("work_date", ""),
            "location": request.form.get("location", ""),
            "work_time": request.form.get("work_time", "")
        }
        session['work_orders'].append(order)
        session.modified = True
        return redirect(url_for('orders'))

    return render_template("orders.html", username=username, orders=session['work_orders'])

# ---------------- Run App ----------------

@app.route('/hybridaction/<path:anything>')
def dummy_hybridaction(anything):
    return {"status": "ignored"}, 200



tasks = [
    {"name": "Tractor Maintenance", "status": "Pending"},
    {"name": "Plow Repair", "status": "Completed"},
    {"name": "Irrigation Pump Check", "status": "Pending"},
]

attendance = [
    {"name": " ", "status": " ", "tool": " "},
    {"name": " ", "status": " ", "tool": " "},
    {"name": " ", "status": " ", "tool": " "},
]

equipment = [
    {"name": "Tractor"},
    {"name": "Plow"},
    {"name": "Irrigation Pump"},
]

orders = [
    {"id": 1, "tool": "Tractor", "quantity": 2, "status": "Pending"},
    {"id": 2, "tool": "Plow", "quantity": 1, "status": "Completed"},
    {"id": 3, "tool": "Irrigation Pump", "quantity": 1, "status": "Pending"},
]

# ------------------ ROUTES ------------------

@app.route("/")
def dashboard_view():
    pending_tasks = [t for t in tasks if t["status"] == "Pending"]
    completed_tasks = [t for t in tasks if t["status"] == "Completed"]
    present_count = sum(1 for a in attendance if a["status"] == "Present")
    absent_count = sum(1 for a in attendance if a["status"] == "Absent")
    return render_template(
        "dashboard.html",
        tasks=tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        attendance=attendance,
        equipment=equipment,
        present_count=present_count,
        absent_count=absent_count
    )

@app.route("/attended")
def attended_view():
    present_count = sum(1 for a in attendance if a["status"] == "Present")
    absent_count = sum(1 for a in attendance if a["status"] == "Absent")
    return render_template(
        "attended.html",
        attendance=attendance,
        present_count=present_count,
        absent_count=absent_count
    )

@app.route("/tasks")
def tasks_view():
    pending_tasks = [t for t in tasks if t["status"] == "Pending"]
    completed_tasks = [t for t in tasks if t["status"] == "Completed"]
    return render_template(
        "tasks.html",
        tasks=tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )

@app.route("/orders")
def orders_view():
    pending_orders = [o for o in orders if o["status"] == "Pending"]
    completed_orders = [o for o in orders if o["status"] == "Completed"]
    return render_template(
        "orders.html",
        orders=orders,
        pending_orders=pending_orders,
        completed_orders=completed_orders
    )


tasks = [
    {"name": "Plowing the field", "status": "Pending"},
    {"name": "Sowing seeds", "status": "Completed"},
    {"name": "Watering crops", "status": "In Progress"},
    {"name": "Fertilizing", "status": "Not Started"},
    {"name": "Harvesting", "status": "Pending"},
    {"name": "Weeding", "status": "In Progress"},
]

@app.route('/')
def attended():
    # Categorize tasks by status
    pending_tasks = [task for task in tasks if task['status'] == 'Pending']
    completed_tasks = [task for task in tasks if task['status'] == 'Completed']
    not_started_tasks = [task for task in tasks if task['status'] == 'Not Started']
    in_progress_tasks = [task for task in tasks if task['status'] == 'In Progress']

    return render_template(
        'dashboard.html',
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        not_started_tasks=not_started_tasks,
        in_progress_tasks=in_progress_tasks
    )
if __name__ == "__main__":
    app.run(debug=True)

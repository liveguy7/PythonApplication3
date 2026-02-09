from flask import Flask, render_template, request, redirect, url_for, flash, session
import pyodbc
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for flash messages

conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAPTOP-L0BU5SNG\\MSSQLSERVER01;"
    "Database=dbSport;"
    "Trusted_Connection=yes;"
)

conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

def get_db_connection(): 
  return pyodbc.connect(
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=LAPTOP-L0BU5SNG\\MSSQLSERVER01;"
    "Database=dbSport;"
    "Trusted_Connection=yes;"
  )
 
def get_products():
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, description, price FROM products")
    rows = cursor.fetchall()

    products = []
    for row in rows:
        products.append({
            "id": row.id,
            "name": row.name,
            "description": row.description,
            "price": float(row.price)
        })
    return products

def get_all_posts():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, content, created_at
        FROM Blog
        ORDER BY created_at DESC
    """)

    posts = cursor.fetchall()
    conn.close()
    return posts


def add_post(title, content):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO Blog (title, content)
        VALUES (?, ?)
    """, (title, content))

    conn.commit()
    conn.close()

def get_latest_posts():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, title, content, created_at
        FROM Blog
        ORDER BY created_at DESC
    """)
    
    posts = cursor.fetchall()
    conn.close()
    return posts

@app.route("/")
def home():
    tmp = render_template("home.html", title="Home")
    return tmp

@app.route("/about")
def about():
    tmp = render_template("about.html", title="About")
    return tmp

@app.route("/privacy")
def privacy():
    tmp = render_template("privacy.html", title="Privacy")
    return tmp

@app.route("/latest")
def latest():
    posts = get_latest_posts()
    return render_template("latest.html", title="Lastest Posts", posts=posts)

@app.route("/calendar")
def calendar():
    var = render_template("calendar.html", title="Events Calendar")
    return var

@app.route("/shop")
def shop():
    products = get_products()  # fetch products from SQL Server
    return render_template("shop.html", products=products)

@app.route("/blog", methods=["GET", "POST"])
def blog():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]

        add_post(title, content)
        return redirect(url_for("blog"))

    posts = get_all_posts()
    return render_template("blog.html", title="Blog", posts=posts)

@app.route("/events")
def events():
    return render_template("events.html", title="Events")

@app.route("/success1")
def success1():
    return render_template("welcome.html", title="Welcome")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = generate_password_hash(request.form["password"])  # hash the password

        try:
            cursor.execute(
                "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                (username, email, password)
            )
            conn.commit()
            flash("Sign Up successful!", "success")
            return redirect(url_for("success1"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("signup.html", title="Sign Up")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, username, password FROM Users WHERE email = ?",
                (email,)
            )
            user = cursor.fetchone()

        if user and check_password_hash(user.password, password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Logged in successfully!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid email or password", "danger")

    return render_template("login.html", title="Login")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


if(__name__ == "__main__"):
    app.run(debug=True)



from db import get_db_connection, close_db_connection
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

connection = get_db_connection()
cursor = connection.cursor()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def apology(message, code=400):
    """Render message as an apology to user."""

    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [
            ("-", "--"),
            (" ", "-"),
            ("_", "__"),
            ("?", "~q"),
            ("%", "~p"),
            ("#", "~h"),
            ("/", "~s"),
            ('"', "''"),
        ]:
            s = s.replace(old, new)
        return s

    return render_template("apology.html", top=code, bottom=escape(message)), code

@app.route("/favorites")
@login_required
def favorites():
    return render_template("favorites.html")

@app.route("/")
@login_required
def index():
    """TODO""" 
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        cursor.execute(
            "SELECT * FROM users WHERE username = %s", (request.form.get("username"),)
        )
        row = cursor.fetchone()  # Obtenha uma única linha

        # Ensure username exists and password is correct
        if row is None or not check_password_hash(
            row[2], request.form.get("password")  # 2 é o índice da coluna 'hash'
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = row[0]  # 0 é o índice da coluna 'id'

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        
        # Verifica se o nome de usuário já está em uso
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        rows = cursor.fetchall()  # Obtém todas as linhas retornadas

        if len(rows) > 0:
            return apology("Username already in use.")

        # Validações
        if not username:
            return apology("Please fill in the username field.")
        if not request.form.get("password"):
            return apology("Please fill in the password field.")
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match.")
        print("HASH: ", generate_password_hash(request.form.get("password")))
        # Inserir novo usuário
        cursor.execute("INSERT INTO users (username, hash) VALUES (%s, %s)", 
                       (username, generate_password_hash(request.form.get("password"))))
        connection.commit()  # Confirma a transação

        return redirect("/login")

    return render_template("register.html")

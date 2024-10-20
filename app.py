from db import get_db_connection
import requests, pickle, os
from flask import Flask, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from dotenv import load_dotenv

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

load_dotenv()
api_key = os.getenv("API_KEY")

connection = get_db_connection()
cursor = connection.cursor()

def fetch_poster(movie_id):
     url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, api_key)
     data=requests.get(url)
     data=data.json()
     poster_path = data['poster_path']
     full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
     return full_path

movies = pickle.load(open("data/movies_list.pkl", 'rb'))
similarity = pickle.load(open("data/similarity.pkl", 'rb'))
movies_list=movies['title'].values


@app.route('/search_movies', methods=['GET'])
def search_movies():
    query = request.args.get('q', '').lower()  # Recebe a query do usuário e transforma em minúsculas
    suggestions = []

    # Filtra os filmes que contêm a string digitada (case-insensitive)
    if query:
        filtered_movies = [movie for movie in movies_list if query in movie.lower()][:5]  # Limita a 5 sugestões

        # Formata as sugestões no formato desejado
        suggestions = [{'value': index + 1, 'text': movie} for index, movie in enumerate(filtered_movies)]
        
    print(suggestions)
    return jsonify(suggestions)

@app.route("/favorites")
def recommend(movie):
    index = movies[movies['title']==movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
    recommend_movie=[]
    recommend_poster=[]
    for i in distance[1:6]:
        movies_id=movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movies_id))
    return recommend_movie, recommend_poster



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
def index():
    """TODO""" 
    return render_template("index.html")

@app.route("/search-movie")
def search_movie():
    query = request.args.get("query", "")
    if query:
        # Filtrar a lista de filmes que começam com o que foi digitado
        suggestions = [movie for movie in movies_list if movie.lower().startswith(query.lower())]
        return jsonify(suggestions[:5])  # Retornar os 5 primeiros
    return jsonify([])


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

from db import get_db_connection
import requests, pickle, os
from flask import Flask, redirect, render_template, request, session, jsonify, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps
from dotenv import load_dotenv

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['DEBUG'] = True
Session(app)

load_dotenv()
api_key = os.getenv("API_KEY")

connection = get_db_connection()
cursor = connection.cursor()

def fetch_poster(movie_id):
     url = "https://api.themoviedb.org/3/movie/{}?api_key={}&language=en-US".format(movie_id, api_key)
     data = requests.get(url)
     data = data.json()
     poster_path = data['poster_path']
     full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
     return full_path

def combine_files(part_count, output_file):
    combined_data = []

    for i in range(1, part_count + 1):
        part_file = f"data/similarity_part{i}.pkl"
        with open(part_file, 'rb') as f:
            combined_data.append(pickle.load(f))

    # Retorne os dados combinados
    return combined_data

# Caminho do arquivo combinado
output_file = "data/similarity_combined.pkl"

# Verifica se o arquivo combinado já existe
if os.path.exists(output_file):
    print(f"O arquivo {output_file} já existe. Não é necessário combinar novamente.")
    similarity = pickle.load(open("data/similarity_combined.pkl", 'rb'))
else:
    # Juntar as 8 partes e salvar como um novo arquivo 'similarity_combined.pkl'
    similarity = combine_files(part_count=8, output_file=output_file)
    
    # Salvar o arquivo combinado
    with open(output_file, 'wb') as f:
        pickle.dump(similarity, f)

    print(f"As partes foram combinadas e salvas em {output_file}.")

movies = pickle.load(open("data/movies_list.pkl", 'rb'))
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

@app.route("/recommend")
def recommend():
    movie = request.args.get("movie")  # Receber o título do filme da solicitação
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    
    recommendations = []
    for i in distance[1:7]:
        movies_id = movies.iloc[i[0]].id
        title = movies.iloc[i[0]].title
        poster = fetch_poster(movies_id)
        
        recommendations.append({
            "title": title,
            "poster": poster
        })

    session["recommendations"] = recommendations  # Armazenar as recomendações na sessão
    return redirect("/")  # Redirecionar para a página inicial


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

@app.route("/favorites", methods=["GET", "POST"])
@login_required
def favorites():
    if request.method == "POST":
        movie_title = request.form.get("movie")

        # Busca o ID do filme através do título
        movie = movies[movies['title'] == movie_title]
        if not movie.empty:
            print("movie: ", movie)
            movie_id = movie.iloc[0]['id']
            print("movie_id: ", movie_id)
            # Adiciona o filme à tabela favorites
            try:
                cursor.execute(
                    "INSERT INTO favorites (user_id, title) VALUES (%s, %s)",
                    (session["user_id"], movie_title)
                )
                connection.commit()  # Confirma a transação
                flash(f'Filme "{movie_title}" adicionado aos favoritos!', 'success')
            except Exception as e:
                flash('Ocorreu um erro ao adicionar o filme aos favoritos. Tente novamente.', 'error')
                print(e)  # Para ajudar na depuração
        else:
            flash('Filme não encontrado. Verifique o título e tente novamente.', 'error')

    # Busca os filmes favoritos do usuário
    cursor.execute(
        "SELECT title FROM favorites WHERE user_id = %s", 
        (session["user_id"],)  # Usando current_user.id
    )
    favorite_movies = cursor.fetchall()  # Obtém todos os filmes favoritos
    print("favorite_movies: ", favorite_movies)
    # Formata a lista para facilitar o uso no template
    favorites_list = [{"title": movie[0], "id": movies[movies['title'] == movie[0]].iloc[0]['id']} for movie in favorite_movies]
    print("favorites_list: ", favorites_list)
    return render_template("favorites.html", favorites=favorites_list, fetch_poster=fetch_poster)



@app.route("/")
def index():
    """Renderizar a página inicial."""
    recommendations = []  # Inicialize a lista de recomendações vazia
    if "recommendations" in session:  # Verifique se há recomendações na sessão
        recommendations = session["recommendations"]  # Recupere as recomendações
        session.pop("recommendations")  # Limpe a sessão após pegar as recomendações

    return render_template("index.html", recommendations=recommendations)  # Passe as recomendações para o template

@app.route("/recommend_by_favorites", methods=["POST"])
@login_required
def recommend_by_favorites():
    cursor.execute(
        "SELECT title FROM favorites WHERE user_id = %s", 
        (session["user_id"],)  # Usando current_user.id
    )
    favorite_movies = cursor.fetchall()  # Obtém todos os filmes favoritos
    print("favorite_movies: ", favorite_movies)
    # Formata a lista para facilitar o uso no template
    favorites_list = [{"title": movie[0], "id": movies[movies['title'] == movie[0]].iloc[0]['id']} for movie in favorite_movies]
    print("favorites1919: ", favorites_list)
    recommendations = []
    for favorite in favorites_list:
        movie_id = favorite["id"]
        print("r movie_id: ", movie_id)
        title = favorite["title"]
        print("r title: ", title)
        # Encontrar recomendações para cada filme favorito
        index = movies[movies['id'] == movie_id].index[0]
        distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
        
        for i in distance[1:7]:  # Pegue os 6 primeiros filmes recomendados
            recommended_movie_id = movies.iloc[i[0]].id
            recommended_movie_title = movies.iloc[i[0]].title
            poster = fetch_poster(recommended_movie_id)
            print("RRRR: ", recommendations)
            recommendations.append({
                "title": recommended_movie_title,
                "poster": poster,
                "reason": f"Because you like {title}"  # Motivo da recomendação
            })
    print("recommendations: ", recommendations)
    session["recommendations"] = recommendations  # Armazena as recomendações
    return redirect("/")  # Redireciona para a página inicial

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


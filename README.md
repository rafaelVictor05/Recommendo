# Recommendo - Movie Recommendation System
#### Video Demo:  <URL HERE>

### Homepage:
![Recommendo Homepage](https://i.imgur.com/jxvF8V6.png)

#### Description:
Recommendo is a movie recommendation system developed using Flask, HTML, Bootstrap, JavaScript, and MySQL. The platform allows users to discover new movies through two key functionalities:

1. **Basic Search**: Users can search for movies without the need to log in. By typing a movie title into the search bar, the system recommends six similar movies based on the provided movie.

2. **Find Based on Favorites**: This feature requires user authentication. Once logged in, users can add movies they like to their list of favorites. Based on these favorites, the system recommends six movies for each movie in the list, with a personalized message like "Because you like *movie x*". 

The system retrieves movie posters from The Movie Database (TMDB) API, and it uses a dataset of 10,000 movies from [Kaggle](https://www.kaggle.com/datasets/moazeldsokyx/imdb-top-10000-movies-dataset) to generate recommendations. I based the project layout on the `layout.html` provided by the CS50 course and used the CS50 `apology` function to return humorous error messages featuring cat memes.

#### Features:
- **Basic Search Function**: Users can type the name of a movie, and the system suggests six similar movies.
- **Find Based on Favorites**: Users can log in, add movies to their favorites list, and receive personalized recommendations.
- **User Authentication**: Users must create an account or log in to use the "Find Based on Favorites" feature.
- **CS50's Apology Function**: I integrated CS50’s `apology` function to display cat meme error messages in case of issues.
- **TMDB API Integration**: Movie posters are fetched dynamically using TMDB’s API.
- **10k Movie Dataset**: The movie recommendations are powered by a Kaggle dataset of 10,000 films, ensuring a diverse set of recommendations.

#### Files:
- `app.py`: This file contains the core logic of the Flask application, including routes for login, registration, 
search, and favorites. It also handles API requests to TMDB for fetching movie posters.
- `db.py`: This file connects to the MySQL database and creates the tables necessary if they weren't created already.
- `layout.html`: The base HTML file for the project, which is built using Bootstrap. This file is derived from CS50's layout template and provides a responsive design for the web app.
- `index.html`: The homepage where users can search for movies or find recommendations based on their favorites.
- `favorites.html`: This page shows the list of favorite movies added by the user and provides personalized recommendations.
- `login.html`: This page receives the user's login information.
- `register.html`: This page receives the user's new account information.
- `apology.html`: This page shows a cat meme with the error message.
- `.env.example`: A sample environment file that users need to copy and rename to `.env` to store sensitive data like the TMDB API key and database credentials.
- `requirements.txt`: This file lists all the dependencies required to run the project.


#### Design Choices:
- **Separation of Concerns**: I ensured that each route in the Flask application handles a specific part of the system’s functionality (e.g., search, recommendations, user management).
- **Error Handling**: Inspired by CS50's `apology` function, I wanted error messages to be not only informative but also fun, which is why I decided to incorporate cat memes.
- **API Integration**: I used the TMDB API for dynamic fetching of movie posters instead of storing them in the local database, ensuring the app remains lightweight and up-to-date.
- **User Experience**: The dual functionality (basic search and personalized recommendations) allows flexibility, providing value for both casual users and logged-in users with specific preferences.

#### Environment Setup:
1. Make a copy of the `.env.example` file and rename it to `.env`.
2. In the `.env` file, add your `API_KEY` from TMDB and fill in your database connection details as shown below:
    ```
    API_KEY=your_tmdb_api_key
    DATABASE_HOST=your_database_host
    DATABASE_USER=your_database_user
    DATABASE_PASSWORD=your_database_password
    DATABASE_NAME=your_database_name
    ```

3. Install the project dependencies by running:
```
pip install -r requirements.txt
```

#### Run the project:
```
flask run
```

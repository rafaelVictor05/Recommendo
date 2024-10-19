import pandas as pd
import requests
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

movies = pd.read_csv('data/dataset.csv')
movies = movies[['id', 'title', 'overview', 'genre']]
movies['tags'] = movies['overview']+movies['genre']
new_data  = movies.drop(columns=['overview', 'genre'])

cv = CountVectorizer(max_features=10000, stop_words='english')
vector = cv.fit_transform(new_data['tags'].values.astype('U')).toarray()
similarity = cosine_similarity(vector)

movies_list=movies['title'].values

def fetch_poster(movie_id):
     url = "https://api.themoviedb.org/3/movie/{}?api_key={}".format(movie_id, api_key)
     data=requests.get(url)
     data=data.json()
     poster_path = data['poster_path']
     full_path = "https://image.tmdb.org/t/p/w500/"+poster_path

     return full_path

def recommend(movie):
    index=movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
    recommend_movie=[]
    recommend_poster=[]

    for i in distance[1:6]:
        movies_id=movies.iloc[i[0]].id
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(fetch_poster(movies_id))
    
    return recommend_movie, recommend_poster



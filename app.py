import streamlit as st
import pickle
import pandas as pd
import requests
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# -------------------- Setup Session with Retry --------------------
session = requests.Session()
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

# -------------------- Poster Cache --------------------
poster_cache = {}


def fetch_poster(movie_id):
    """Fetch poster URL from TMDB with retry, caching, and delay"""
    if movie_id in poster_cache:
        return poster_cache[movie_id]

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=f3d269f30e79647a09114a69b142d4e0&language=en-US"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
        poster_cache[movie_id] = poster_url
        time.sleep(0.5)  # avoid rapid-fire requests
        return poster_url
    except requests.exceptions.RequestException:
        return "https://via.placeholder.com/500x750?text=No+Image"


# -------------------- Recommendation Function --------------------
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommend_movies = []
    recommend_movies_posters = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        recommend_movies.append(movies.iloc[i[0]].title)
        recommend_movies_posters.append(fetch_poster(movie_id))

    return recommend_movies, recommend_movies_posters


# -------------------- Load Data --------------------
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

# -------------------- Streamlit App --------------------
st.title('Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters = recommend(selected_movie_name)

    col1, col2, col3, col4, col5 = st.columns(5)

    for col, name, poster in zip([col1, col2, col3, col4, col5], names, posters):
        with col:
            st.text(name)
            st.image(poster)

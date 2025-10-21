import streamlit as st
import pickle
import pandas as pd
import requests

# --- Load Data ---
movies_dict = pickle.load(open('movies.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))


# --- Fetch Poster and IMDb rating ---
def fetch_movie_details(movie_id):
    api_key = "01b397bf9e3c76a160ec9c39423731d2"  # replace with your TMDB key or use st.secrets
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()

    poster = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    rating = round(data['vote_average'], 1)  # IMDb-like rating (scale 0–10)

    return poster, rating


# --- Recommendation Function ---
def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_posters = []
    recommended_ratings = []

    for i in movies_list:
        movie_id = movies.iloc[i[0]].movie_id
        poster, rating = fetch_movie_details(movie_id)
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_posters.append(poster)
        recommended_ratings.append(rating)

    return recommended_movies, recommended_posters, recommended_ratings


# --- Streamlit UI ---
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters, ratings = recommend(selected_movie_name)

    # Display all 5 movies in one row
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.image(posters[i], use_container_width=True)
            st.markdown(f"**{names[i]}**")
            st.markdown(f"⭐ TMDb Rating: **{ratings[i]} / 10**")

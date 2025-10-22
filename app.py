import streamlit as st
import pandas as pd
import pickle
import requests
import os

# -----------------------------
# Dropbox direct download links
# -----------------------------
movies_url = "https://www.dropbox.com/scl/fi/7wp3ysme1m8vg0t2x9om2/movies.pkl?rlkey=5pfeearsfl01rmcl8njxjb284&st=eyrl8fqn&dl=1"       # Replace with your Dropbox link
similarity_url = "https://www.dropbox.com/scl/fi/y5yx8wyuv8pzwjm5fluc0/similarity.pkl?rlkey=68aozdy3swnvtarwui43bxh17&st=8y3qskbe&dl=1" # Replace with your Dropbox link

# -----------------------------
# Download function
# -----------------------------
def download_file(url, filename):
    if not os.path.exists(filename):
        r = requests.get(url, allow_redirects=True)
        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"{filename} downloaded successfully.")
        else:
            raise Exception(f"Failed to download {filename}, status code {r.status_code}")

# Download files if not exist
download_file(movies_url, "movies.pkl")
download_file(similarity_url, "similarity.pkl")

# -----------------------------
# Load Data
# -----------------------------
movies_dict = pickle.load(open("movies.pkl", "rb"))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open("similarity.pkl", "rb"))

# -----------------------------
# Fetch Poster and TMDb rating
# -----------------------------
def fetch_movie_details(movie_id):
    api_key = "01b397bf9e3c76a160ec9c39423731d2"  # Replace with your TMDb API key
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()

    poster = "https://image.tmdb.org/t/p/w500/" + data['poster_path']
    rating = round(data['vote_average'], 1)  # TMDb rating
    return poster, rating

# -----------------------------
# Recommendation Function
# -----------------------------
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

# -----------------------------
# Streamlit UI
# -----------------------------
st.set_page_config(page_title="Movie Recommender", layout="wide")
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    "Select a movie to get recommendations:",
    movies['title'].values
)

if st.button("Recommend"):
    names, posters, ratings = recommend(selected_movie_name)

    # Display all 5 recommendations in a single row
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            st.image(posters[i], use_container_width=True)
            st.markdown(f"**{names[i]}**")
            st.markdown(f"⭐ TMDb Rating: **{ratings[i]} / 10**")

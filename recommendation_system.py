import pandas as pd
import mysql.connector
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

class GameRecommender:
    """
    An upgraded content-based recommendation system that uses a composite user profile
    and feature weighting for more accurate recommendations.
    """
    def __init__(self, db_config):
        self.db_config = db_config
        self.connection = None
        self.games_df = None
        self.reviews_df = None
        self.wishlist_df = None
        self.similarity_matrix = None
        self.game_vectors = None # We'll store the vectors themselves now
        self.game_indices = None
        self._connect_to_db()
        self._load_and_prepare_data()
        self._build_model()

    def _connect_to_db(self):
        try:
            self.connection = mysql.connector.connect(**self.db_config)
            print("[AI System] Successfully connected to the database.")
        except mysql.connector.Error as err:
            print(f"[AI System] Error connecting to database: {err}")
            raise

    def _load_and_prepare_data(self):
        """Loads data and prepares it with feature weighting."""
        if not self.connection:
            return

        games_query = """
            SELECT g.id, g.title, g.publisher, g.release_year, g.image, g.description, 
                   gn.name as genre, p.name as platform, g.developer_id
            FROM Games g
            LEFT JOIN Genres gn ON g.genre_id = gn.id
            LEFT JOIN Platforms p ON g.platform_id = p.id;
        """
        self.games_df = pd.read_sql(games_query, self.connection)
        self.reviews_df = pd.read_sql("SELECT user_id, game_id, rating FROM Reviews;", self.connection)
        self.wishlist_df = pd.read_sql("SELECT user_id, game_id FROM Wishlist;", self.connection)
        
        for col in ['publisher', 'genre', 'platform']:
            self.games_df[col] = self.games_df[col].fillna('')

        # --- IMPROVEMENT 1: FEATURE WEIGHTING ---
        # We repeat the genre to give it more importance in the similarity calculation.
        self.games_df['tags'] = (self.games_df['genre'] + ' ') * 3 + self.games_df['platform'] + ' ' + self.games_df['publisher']
        self.games_df['tags'] = self.games_df['tags'].str.lower()
        
        print("[AI System] Data loaded and prepared successfully.")

    def _build_model(self):
        if self.games_df is None:
            return

        cv = CountVectorizer(max_features=5000, stop_words='english')
        # Store the vectors for creating composite profiles later
        self.game_vectors = cv.fit_transform(self.games_df['tags']).toarray()

        # The similarity matrix is still useful for game-to-game lookups if needed
        self.similarity_matrix = cosine_similarity(self.game_vectors)

        self.game_indices = pd.Series(self.games_df.index, index=self.games_df['id']).to_dict()
        print("[AI System] Recommendation model built successfully.")

    def get_recommendations(self, user_id, n_recommendations=10):
        """
        Generates recommendations based on a composite profile of all liked games.
        """
        high_rated_games = self.reviews_df[(self.reviews_df['user_id'] == user_id) & (self.reviews_df['rating'] >= 4)]
        wishlisted_games = self.wishlist_df[self.wishlist_df['user_id'] == user_id]
        user_liked_game_ids = set(high_rated_games['game_id']).union(set(wishlisted_games['game_id']))

        if not user_liked_game_ids:
            # Cold Start: Recommend popular games
            print(f"[AI System] User {user_id} has no liked games. Recommending popular games.")
            avg_ratings = self.reviews_df.groupby('game_id')['rating'].mean().sort_values(ascending=False)
            top_game_ids = avg_ratings.head(n_recommendations).index.tolist()
            return self.games_df[self.games_df['id'].isin(top_game_ids)].to_dict(orient='records')

        # --- IMPROVEMENT 2: COMPOSITE TASTE PROFILE ---
        liked_indices = [self.game_indices[game_id] for game_id in user_liked_game_ids if game_id in self.game_indices]
        if not liked_indices:
            return [] # User's liked games are not in the dataset

        # Create the average taste vector
        user_profile_vector = np.mean(self.game_vectors[liked_indices], axis=0)

        # Calculate similarity of all games to the user's composite profile
        # Reshape vector to be a 2D array for cosine_similarity function
        similarity_scores = cosine_similarity(user_profile_vector.reshape(1, -1), self.game_vectors)

        # Get scores as a flat list and enumerate to keep track of game indices
        sorted_games = sorted(list(enumerate(similarity_scores[0])), key=lambda x: x[1], reverse=True)

        recommendations = []
        for game_index, score in sorted_games:
            game_id = self.games_df.iloc[game_index]['id']
            if game_id not in user_liked_game_ids:
                recommendations.append(self.games_df.iloc[game_index].to_dict())
            if len(recommendations) >= n_recommendations:
                break
        
        return recommendations

    def close_connection(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("[AI System] Database connection closed.")


from flask import Flask, jsonify
from flask_cors import CORS
from recommendation_system import GameRecommender
import numpy as np # <-- 1. IMPORT NUMPY

# --- Database Configuration ---
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'allmight@18',
    'database': 'game_library'
}

app = Flask(__name__)
CORS(app)

print("Initializing AI Recommendation Server...")
try:
    recommender = GameRecommender(DB_CONFIG)
    print("AI Server is ready to receive requests on port 5001.")
except Exception as e:
    print(f"FATAL: Could not initialize the recommender system: {e}")
    recommender = None

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_user_recommendations(user_id):
    """
    API endpoint to get game recommendations for a specific user.
    """
    if not recommender:
        return jsonify({"error": "The recommendation system is currently unavailable."}), 503
        
    try:
        recommendations = recommender.get_recommendations(user_id, n_recommendations=10)
        
        # --- 2. ADD THIS FIX ---
        # Loop through each recommended game to clean the data before sending.
        # This replaces any 'NaN' values with 'None', which becomes 'null' in JSON.
        for game in recommendations:
            if 'developer_id' in game and np.isnan(game['developer_id']):
                game['developer_id'] = None
        # --- END OF FIX ---

        return jsonify({"recommendations": recommendations})
        
    except Exception as e:
        print(f"An error occurred while getting recommendations for user {user_id}: {e}")
        return jsonify({"error": "An internal error occurred on the AI server."}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)


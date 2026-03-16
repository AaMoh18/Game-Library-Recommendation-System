import requests
import mysql.connector
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal

# --- Database Configuration ---
db_config = {
    'user': 'root',
    'password': 'allmight@18',  # *** UPDATE THIS WITH YOUR MYSQL PASSWORD ***
    'host': '127.0.0.1',
    'database': 'game_library',
    'raise_on_warnings': True
}

# --- AI Server Configuration ---
# This is the address of your separate AI server
AI_API_URL = 'http://127.0.0.1:5001'

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def get_db_connection():
    """Establishes and returns a new database connection."""
    return mysql.connector.connect(**db_config)

# --- Helper Function ---
def get_user_role(user_id):
    """Fetches the role of a user from the database, with a hardcoded admin check."""
    if not user_id: return None
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch email along with role to check for the hardcoded admin
        cursor.execute("SELECT role, email FROM Users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        # Hardcoded admin check
        if user and user['email'] == 'admin@example.com':
            return 'admin'
            
        return user['role'] if user else None
    finally:
        cursor.close()
        conn.close()


# --- Authentication Endpoints ---

@app.route('/api/register', methods=['POST'])
def register():
    """API endpoint for user registration with password hashing."""
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({"error": "Name, email, and password are required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({"error": "Email already registered"}), 409

        hashed_password = generate_password_hash(password)
        sql = "INSERT INTO Users (name, email, password_hash) VALUES (%s, %s, %s)"
        cursor.execute(sql, (name, email, hashed_password))
        conn.commit()
        return jsonify({"message": "Registration successful"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """API endpoint for user login, returns user role with a hardcoded admin check."""
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, password_hash, role, email FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user['password_hash'], password):
            
            # Hardcoded admin check: if email matches, override the role
            user_role = 'admin' if user['email'] == 'admin@example.com' else user['role']
            
            return jsonify({
                "message": "Login successful", 
                "user": {
                    "id": user['id'], 
                    "name": user['name'],
                    "role": user_role
                }
            }), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# --- Account Management Endpoints ---

@app.route('/api/user/<int:user_id>/change-username', methods=['PUT'])
def change_username(user_id):
    data = request.json
    new_name = data.get('name')
    if not new_name:
        return jsonify({"error": "New name is required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET name = %s WHERE id = %s", (new_name, user_id))
        conn.commit()
        return jsonify({"message": "Username updated successfully"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/user/<int:user_id>/change-password', methods=['PUT'])
def change_password(user_id):
    data = request.json
    new_password = data.get('password')
    if not new_password:
        return jsonify({"error": "New password is required"}), 400
        
    hashed_password = generate_password_hash(new_password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET password_hash = %s WHERE id = %s", (hashed_password, user_id))
        conn.commit()
        return jsonify({"message": "Password updated successfully"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/user/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Reviews WHERE user_id = %s", (user_id,))
        cursor.execute("DELETE FROM Users WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "Account deleted successfully"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/user/<int:user_id>/convert-to-developer', methods=['POST'])
def convert_to_developer(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE Users SET role = 'developer' WHERE id = %s", (user_id,))
        conn.commit()
        return jsonify({"message": "Account successfully upgraded to a developer account!"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# --- Core Content Endpoints ---

@app.route('/api/genres', methods=['GET'])
def get_genres():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name FROM Genres")
        genres = cursor.fetchall()
        return jsonify(genres)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/games', methods=['GET'])
def get_all_games():
    search_query = request.args.get('q', '')
    genre_ids_str = request.args.get('genres', '')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql_query = """
            SELECT
                g.id, g.title, g.release_year, g.publisher, g.image,
                g.description, gn.name AS genre, p.name AS platform, g.developer_id
            FROM Games g
            JOIN Genres gn ON g.genre_id = gn.id
            JOIN Platforms p ON g.platform_id = p.id
            WHERE 1=1
        """
        params = []
        if search_query:
            sql_query += " AND g.title LIKE %s"
            params.append(f"%{search_query}%")
        if genre_ids_str:
            genre_ids = [int(g_id) for g_id in genre_ids_str.split(',')]
            placeholders = ','.join(['%s'] * len(genre_ids))
            sql_query += f" AND gn.id IN ({placeholders})"
            params.extend(genre_ids)

        cursor.execute(sql_query, tuple(params))
        games = cursor.fetchall()
        return jsonify(games)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# --- User Interaction Endpoints (Reviews, Wishlist, Recommendations) ---


@app.route('/api/popular-games', methods=['GET'])
def get_popular_games():
    """Fetches games and sorts them based on popularity metrics."""
    sort_by = request.args.get('sort_by', 'rating')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT
                g.id, g.title, g.release_year, g.publisher, g.image,
                g.description, gn.name AS genre, p.name AS platform, g.developer_id,
                COUNT(DISTINCT r.id) as review_count,
                AVG(r.rating) as avg_rating,
                (SELECT COUNT(*) FROM Wishlist w WHERE w.game_id = g.id) as wishlist_count
            FROM Games g
            LEFT JOIN Genres gn ON g.genre_id = gn.id
            LEFT JOIN Platforms p ON g.platform_id = p.id
            LEFT JOIN Reviews r ON g.id = r.game_id
            GROUP BY g.id, gn.name, p.name
        """
        
        if sort_by == 'reviews':
            query += " ORDER BY review_count DESC, avg_rating DESC"
        elif sort_by == 'wishlist':
            query += " ORDER BY wishlist_count DESC, avg_rating DESC"
        else:
            query += " ORDER BY avg_rating DESC, review_count DESC"

        cursor.execute(query)
        games = cursor.fetchall()
        for game in games:
            if isinstance(game.get('avg_rating'), Decimal):
                game['avg_rating'] = float(game['avg_rating'])
            if game.get('avg_rating') is None:
                game['avg_rating'] = 0
        return jsonify(games)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/reviews', methods=['POST'])
def add_review():
    data = request.json
    user_id, game_id, rating, review_text = data.get('user_id'), data.get('game_id'), data.get('rating'), data.get('review_text')

    if not all([user_id, game_id, rating, review_text]):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = "INSERT INTO Reviews (user_id, game_id, rating, review_text, date) VALUES (%s, %s, %s, %s, CURDATE())"
        cursor.execute(sql, (user_id, game_id, rating, review_text))
        conn.commit()
        return jsonify({"message": "Review added successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/reviews/<int:game_id>', methods=['GET'])
def get_reviews(game_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT r.rating, r.review_text, r.date, u.name AS user_name
            FROM Reviews r
            JOIN Users u ON r.user_id = u.id
            WHERE r.game_id = %s ORDER BY r.date DESC
        """
        cursor.execute(sql, (game_id,))
        reviews = cursor.fetchall()
        return jsonify(reviews)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/wishlist', methods=['POST'])
def add_to_wishlist():
    data = request.json
    user_id, game_id = data.get('user_id'), data.get('game_id')
    if not all([user_id, game_id]):
        return jsonify({"error": "User ID and Game ID are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO Wishlist (user_id, game_id) VALUES (%s, %s)", (user_id, game_id))
        conn.commit()
        return jsonify({"message": "Game added to wishlist"}), 201
    except mysql.connector.Error as err:
        if err.errno == 1062:
            return jsonify({"error": "Game already in wishlist"}), 409
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/wishlist/<int:user_id>/<int:game_id>', methods=['DELETE'])
def remove_from_wishlist(user_id, game_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Wishlist WHERE user_id = %s AND game_id = %s", (user_id, game_id))
        conn.commit()
        if cursor.rowcount == 0:
            return jsonify({"error": "Item not found in wishlist"}), 404
        return jsonify({"message": "Game removed from wishlist"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/wishlist/<int:user_id>', methods=['GET'])
def get_wishlist(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT 
                g.id, g.title, g.image, gn.name AS genre, p.name AS platform, g.publisher, g.release_year
            FROM Wishlist w
            JOIN Games g ON w.game_id = g.id
            JOIN Genres gn ON g.genre_id = gn.id
            JOIN Platforms p ON g.platform_id = p.id
            WHERE w.user_id = %s
        """, (user_id,))
        wishlist_games = cursor.fetchall()
        
        cursor.execute("SELECT game_id FROM Reviews WHERE user_id = %s", (user_id,))
        reviewed_games_raw = cursor.fetchall()
        reviewed_game_ids = [item['game_id'] for item in reviewed_games_raw]

        return jsonify({"wishlist": wishlist_games, "reviewed_game_ids": reviewed_game_ids})
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """
    This endpoint now acts as a proxy. It forwards the request to the dedicated AI server.
    """
    try:
        # 1. Forward the request to the AI server running on port 5001
        # We assume the AI server's response looks like: {"recommendations": [...]}
        # In app.py
        ai_response = requests.get(f"{AI_API_URL}/api/recommendations/{user_id}")
        ai_response.raise_for_status()  # This will raise an exception for HTTP errors (4xx or 5xx)
        
        # 2. Get the JSON data from the AI server's response
        data = ai_response.json()
        
        # 3. Extract just the list of games and return it.
        # This matches what your frontend (index.html) expects.
        return jsonify(data.get('recommendations', []))

    except requests.exceptions.RequestException as e:
        # This error happens if the AI server is down or there's a network issue
        print(f"Error contacting AI server: {e}")
        return jsonify({"error": "The recommendation service is temporarily unavailable."}), 503
    except Exception as e:
        print(f"An unexpected error occurred in the proxy: {e}")
        return jsonify({"error": "An internal server error occurred."}), 500

# --- Developer-Only Endpoints ---

@app.route('/api/games', methods=['POST'])
def add_game():
    data = request.json
    developer_id = data.get('developer_id')
    
    # FIX: Allow 'admin' to add games as well
    user_role = get_user_role(developer_id)
    if user_role not in ['developer', 'admin']:
        return jsonify({"error": "Unauthorized: Only developers or admins can add games"}), 403

    title, genre_id, platform_id = data.get('title'), data.get('genre_id'), data.get('platform_id')
    release_year, publisher = data.get('release_year'), data.get('publisher')
    image, description = data.get('image'), data.get('description')
    
    if not all([title, genre_id, platform_id, release_year, publisher]):
        return jsonify({"error": "Missing required game fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        sql = """INSERT INTO Games 
                 (title, genre_id, platform_id, release_year, publisher, image, description, developer_id) 
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        params = (title, genre_id, platform_id, release_year, publisher, image, description, developer_id)
        cursor.execute(sql, params)
        conn.commit()
        return jsonify({"message": "Game added successfully"}), 201
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/games/<int:game_id>', methods=['PUT'])
def edit_game(game_id):
    data = request.json
    developer_id = data.get('developer_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT developer_id FROM Games WHERE id = %s", (game_id,))
        game = cursor.fetchone()

        # Allow edit if user is the owner OR if the user is an admin
        user_role = get_user_role(developer_id)
        is_owner = game and game['developer_id'] == developer_id
        
        if not (is_owner or user_role == 'admin'):
            return jsonify({"error": "Unauthorized: You can only edit your own games"}), 403

        update_fields = []
        params = []
        for field in ['title', 'genre_id', 'platform_id', 'release_year', 'publisher', 'image', 'description']:
            if field in data:
                update_fields.append(f"{field} = %s")
                params.append(data[field])
        
        if not update_fields:
            return jsonify({"error": "No fields to update"}), 400

        params.append(game_id)
        sql = f"UPDATE Games SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor_update = conn.cursor()
        cursor_update.execute(sql, tuple(params))
        conn.commit()
        cursor_update.close()
        
        return jsonify({"message": "Game updated successfully"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route('/api/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    """Deletes a game and all its associated reviews."""
    data = request.json
    developer_id = data.get('developer_id')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT developer_id FROM Games WHERE id = %s", (game_id,))
        game = cursor.fetchone()
        if not game or game['developer_id'] != developer_id:
            return jsonify({"error": "Unauthorized: You can only delete your own games"}), 403
        
        dml_cursor = conn.cursor()
        dml_cursor.execute("DELETE FROM Reviews WHERE game_id = %s", (game_id,))
        dml_cursor.execute("DELETE FROM Wishlist WHERE game_id = %s", (game_id,))
        dml_cursor.execute("DELETE FROM Games WHERE id = %s", (game_id,))
        
        conn.commit()
        dml_cursor.close()

        return jsonify({"message": "Game deleted successfully"}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/developer/<int:developer_id>/analytics', methods=['GET'])
def get_game_analytics(developer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        sql = """
            SELECT 
                g.id, g.title,
                COUNT(DISTINCT r.id) AS total_reviews,
                AVG(r.rating) AS average_rating,
                (SELECT COUNT(*) FROM Wishlist w WHERE w.game_id = g.id) AS total_wishlists
            FROM Games g
            LEFT JOIN Reviews r ON g.id = r.game_id
            WHERE g.developer_id = %s
            GROUP BY g.id, g.title
            ORDER BY total_reviews DESC;
        """
        cursor.execute(sql, (developer_id,))
        analytics = cursor.fetchall()
        for item in analytics:
            if isinstance(item['average_rating'], Decimal):
                item['average_rating'] = float(item['average_rating'])
            elif item['average_rating'] is None:
                item['average_rating'] = 0
        return jsonify(analytics)
    except mysql.connector.Error as err:
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# --- Admin-Only Endpoint ---
@app.route('/api/admin/games/<int:game_id>', methods=['DELETE'])
def admin_delete_game(game_id):
    """Admin endpoint to delete any game."""
    data = request.json
    admin_id = data.get('admin_id')

    if get_user_role(admin_id) != 'admin':
        return jsonify({"error": "Unauthorized: Admin access required"}), 403
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Reviews WHERE game_id = %s", (game_id,))
        cursor.execute("DELETE FROM Wishlist WHERE game_id = %s", (game_id,))
        cursor.execute("DELETE FROM Games WHERE id = %s", (game_id,))
        
        conn.commit()
        return jsonify({"message": "Game and all associated data deleted successfully by admin"}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)


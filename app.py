from flask import Flask, request, jsonify, render_template  # Import necessary modules from Flask and other packages
from flask_cors import CORS  # Import CORS module to handle cross-origin requests
from pymongo import MongoClient  # Import MongoClient to connect to MongoDB

app = Flask(__name__)  # Create a Flask application instance
CORS(app)  # Enable CORS for the app

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Connect to MongoDB server
db = client.trivia_game  # Select the 'trivia_game' database

# Serve the frontend
@app.route('/')
def index():
    return render_template('index.html')  # Serve the main HTML file

# Register a new user
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    if db.users.find_one({'username': username}):  # Check if the user already exists
        return jsonify({'message': 'User already exists'}), 400
    db.users.insert_one({'username': username, 'score': 0})  # Insert new user with a score of 0
    return jsonify({'message': 'User registered successfully'}), 201

# Fetch a random state question
@app.route('/question', methods=['GET'])
def get_question():
    state = db.states.aggregate([{'$sample': {'size': 1}}]).next()  # Get a random state
    return jsonify({'state': state['name'], 'image_url': state['image_url']})  # Return state name and image URL

# Fetch a random capital question
@app.route('/reverse_question', methods=['GET'])
def get_reverse_question():
    state = db.states.aggregate([{'$sample': {'size': 1}}]).next()  # Get a random state
    return jsonify({'capital': state['capital'], 'image_url': state['image_url']})  # Return capital name and image URL

# Submit an answer for state question
@app.route('/answer', methods=['POST'])
def answer_question():
    data = request.json
    username = data.get('username')
    state = data.get('state')
    capital = data.get('capital')

    user = db.users.find_one({'username': username})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    correct_answer = db.states.find_one({'name': state})['capital']
    if capital.lower() == correct_answer.lower():
        db.users.update_one({'username': username}, {'$inc': {'score': 1}})
        return jsonify({'message': 'Correct!', 'new_score': user['score'] + 1}), 200
    return jsonify({'message': 'Incorrect!', 'correct_answer': correct_answer}), 200

# Submit an answer for capital question
@app.route('/reverse_answer', methods=['POST'])
def answer_reverse_question():
    data = request.json
    username = data.get('username')
    state = data.get('state')
    capital = data.get('capital')

    user = db.users.find_one({'username': username})
    if not user:
        return jsonify({'message': 'User not found'}), 404

    correct_answer = db.states.find_one({'capital': capital})['name']
    if state.lower() == correct_answer.lower():
        db.users.update_one({'username': username}, {'$inc': {'score': 1}})
        return jsonify({'message': 'Correct!', 'new_score': user['score'] + 1}), 200
    return jsonify({'message': 'Incorrect!', 'correct_answer': correct_answer}), 200

# Get the leaderboard
@app.route('/leaderboard', methods=['GET'])
def leaderboard():
    users = list(db.users.find().sort('score', -1).limit(10))  # Get top 10 users sorted by score
    return jsonify(users)  # Return the leaderboard

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application

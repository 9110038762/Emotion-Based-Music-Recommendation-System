from flask import Flask, render_template, request, jsonify
from recommender.engine import RecommendationEngine

app = Flask(__name__)

# Initialize recommendation engine
try:
    engine = RecommendationEngine()
except Exception as e:
    print(f"Error initializing RecommendationEngine: {e}")
    engine = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def recommend():
    if not engine:
        return jsonify({"error": "Fuzzy recommendation engine failed to initialize. Check console logs."}), 500
        
    data = request.get_json() or {}
    
    # Retrieve and validate inputs
    try:
        current_valence = float(data.get('valence', 5.0))
        current_arousal = float(data.get('arousal', 5.0))
        strategy = data.get('strategy', 'match')
    except (TypeError, ValueError):
        return jsonify({"error": "Valence and Arousal must be numbers between 0 and 10."}), 400

    # Validate range
    if not (0.0 <= current_valence <= 10.0) or not (0.0 <= current_arousal <= 10.0):
        return jsonify({"error": "Valence and Arousal must be between 0.0 and 10.0."}), 400

    # Strategies must be in the valid list
    valid_strategies = ['match', 'boost', 'calm', 'vent']
    if strategy not in valid_strategies:
        strategy = 'match'

    try:
        # Run recommendation
        results = engine.recommend(
            current_valence=current_valence,
            current_arousal=current_arousal,
            strategy=strategy,
            num_recommendations=9  # Return 9 tracks for a clean responsive grid layout
        )
        return jsonify(results)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Failed to calculate recommendations: {str(e)}"}), 500

if __name__ == '__main__':
    # Run Flask local development server
    app.run(host='127.0.0.1', port=5001, debug=True)

import numpy as np
from recommender.tracks import TRACKS
from recommender.fuzzy_system import EmotionFuzzySystem

class RecommendationEngine:
    def __init__(self):
        # Initialize the fuzzy logic controller
        self.fuzzy_system = EmotionFuzzySystem()

    def map_mood_strategy(self, current_valence, current_arousal, strategy):
        """
        Maps the user's current mood and chosen strategy to a desired music profile
        (target valence and arousal coordinates in the [0, 10] fuzzy space).
        """
        # Ensure inputs are floats and in range
        v = float(np.clip(current_valence, 0.0, 10.0))
        a = float(np.clip(current_arousal, 0.0, 10.0))

        if strategy == "match":
            # Direct representation of current mood
            target_v = v
            target_a = a
            strategy_name = "Match Mood"
            strategy_desc = "Finding music that mirrors your current emotional state."

        elif strategy == "boost":
            # Elevate valence (happiness) and ensure a moderate-high energy (arousal)
            target_v = max(v + (10.0 - v) * 0.6, 7.0)
            target_a = max(a + (10.0 - a) * 0.3, 6.0)
            strategy_name = "Boost Mood"
            strategy_desc = "Steering toward positive, uplifting, and energetic tracks to elevate your spirits."

        elif strategy == "calm":
            # Moderate-high valence (peaceful) and significantly lower arousal (calming down)
            target_v = max(v, 6.0)
            target_a = min(a * 0.4, 3.0)
            strategy_name = "Calm Down"
            strategy_desc = "Steering toward tranquil, soothing, and relaxing tracks to lower tension."

        elif strategy == "vent":
            # Low valence (cathartic/dark) and very high energy/arousal (high intensity release)
            target_v = min(v, 4.0)
            target_a = max(a, 8.0)
            strategy_name = "Vent (Catharsis)"
            strategy_desc = "Releasing intense feelings with raw, high-energy, and heavy tracks."
        
        else:
            # Default to match
            target_v = v
            target_a = a
            strategy_name = "Match Mood"
            strategy_desc = "Finding music that mirrors your current emotional state."

        return {
            "target_valence": float(np.clip(target_v, 0.0, 10.0)),
            "target_arousal": float(np.clip(target_a, 0.0, 10.0)),
            "name": strategy_name,
            "description": strategy_desc
        }

    def recommend(self, current_valence, current_arousal, strategy="match", num_recommendations=5):
        """
        Processes inputs through the strategy mapper and fuzzy system, matches against the database,
        and returns the top recommendations alongside the FIS visualization image.
        """
        # 1. Map strategy to target coordinates
        strategy_info = self.map_mood_strategy(current_valence, current_arousal, strategy)
        target_v = strategy_info["target_valence"]
        target_a = strategy_info["target_arousal"]

        # 2. Run fuzzy inference to get target audio features
        target_features = self.fuzzy_system.evaluate(target_v, target_a)

        # 3. Calculate distance from target features to all tracks in database
        # Feature weights: Valence and Energy are key indicators of mood, 
        # while Danceability and Tempo add secondary rhythmic alignment.
        weights = {
            'valence': 1.2,
            'energy': 1.2,
            'danceability': 0.8,
            'tempo': 0.8
        }
        
        # Max theoretical distance for normalization
        max_dist = np.sqrt(
            (weights['valence'] * 1.0) ** 2 +
            (weights['energy'] * 1.0) ** 2 +
            (weights['danceability'] * 1.0) ** 2 +
            (weights['tempo'] * 1.0) ** 2
        )

        results = []
        for track in TRACKS:
            # Euclidean distance calculation
            d_val = weights['valence'] * (target_features['valence'] - track['energy'])  # wait, valence matches valence!
            # Let's be careful. The track has 'valence' and 'energy', the target_features also has 'valence' and 'energy'!
            # Let's map target valence to track valence, target energy to track energy, etc.
            d_val = weights['valence'] * (target_features['valence'] - track['valence'])
            d_ene = weights['energy'] * (target_features['energy'] - track['energy'])
            d_dan = weights['danceability'] * (target_features['danceability'] - track['danceability'])
            d_tem = weights['tempo'] * (target_features['tempo'] - track['tempo'])

            distance = np.sqrt(d_val**2 + d_ene**2 + d_dan**2 + d_tem**2)
            # Match percentage (similarity score)
            match_score = float(100.0 * (1.0 - (distance / max_dist)))

            track_info = track.copy()
            track_info['distance'] = float(distance)
            track_info['match_score'] = round(match_score, 1)
            results.append(track_info)

        # Sort tracks by match score descending (highest similarity first)
        results.sort(key=lambda x: x['match_score'], reverse=True)
        top_recommendations = results[:num_recommendations]

        # 4. Generate the base64 plot for the FIS State
        plot_base64 = self.fuzzy_system.get_all_plots_base64(
            val_val=target_v,
            aro_val=target_a,
            outputs=target_features
        )

        return {
            "strategy": strategy_info,
            "target_features": target_features,
            "recommendations": top_recommendations,
            "plot_image": plot_base64
        }

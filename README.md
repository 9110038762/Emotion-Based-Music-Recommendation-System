# VibeFuzzy: Emotion-Based Music Recommendation System

A complete Python web application that recommends music tracks based on the user's emotional state, powered by **Fuzzy Logic** (`scikit-fuzzy`) and **NumPy**. The project translates subjective emotional inputs into objective audio target parameters, searches a track library, and visualizes the fuzzy system states in real-time.

---

## 🌟 Key Features

1. **Circumplex Mood Mapping**: Translates user inputs of **Valence** (pleasure/happiness) and **Arousal** (physiological energy) into emotional labels based on the classical psychological *Russell Circumplex Model of Affect*.
2. **Fuzzy Logic Controller (FLC)**: Takes subjective, non-binary inputs (0.0 to 10.0) and models them into fuzzy sets (`low`, `medium`, `high`) using overlapping triangular membership functions.
3. **Four Recommendation Strategies**:
   - `Match Mood`: Recommends songs that mirror the user's current emotional state.
   - `Boost Mood`: Cognitive shift designed to elevate Valence (positivity) and Arousal (active energy).
   - `Calm Down`: Cognitive shift designed to increase Valence while dropping Arousal to a tranquil level.
   - `Vent (Catharsis)`: Recommends intense, low-valence, high-energy music to help release tension.
4. **Euclidean Matching Engine**: Matches the defuzzified target coordinates (Valence, Energy, Danceability, Tempo) against a track library using weighted Euclidean distance and returns recommendations sorted by matching score (%).
5. **Real-time State Visualization**: Generates a 2x3 grid using `matplotlib` showing the user's inputs on the antecedent fuzzy sets and the defuzzified results on the consequent fuzzy sets, rendered directly on the webpage.
6. **Premium Responsive UI**: Sleek, glassmorphism-based dark mode interface with micro-interactions, custom glowing sliders, and animated song cards.

---

## 📂 Project Structure

```text
emotion-music-recommender/
│
├── recommender/
│   ├── __init__.py         # Exposes the RecommendationEngine class
│   ├── fuzzy_system.py     # Fuzzy Set definition, rules, evaluation, and plot generation
│   ├── engine.py           # Cognitive mapping strategies and track distance matching
│   └── tracks.py           # Track library (database) with pre-evaluated audio features
│
├── templates/
│   └── index.html          # Beautiful HTML5 layout and documentation
│
├── static/
│   ├── css/
│   │   └── style.css       # Premium glassmorphic design, custom sliders, and glows
│   └── js/
│       └── main.js         # Interactive slider events, AJAX requests, and dynamic DOM rendering
│
├── requirements.txt        # Python dependency list
├── app.py                  # Flask web server entrypoint
└── README.md               # System and setup documentation
```

---

## 🛠️ Fuzzy System Architecture

### 1. Variables & Membership Sets
- **Inputs (Antecedents)** [0.0 - 10.0]:
  - `valence_in`: Degrees of pleasure/happiness (`low`, `medium`, `high`)
  - `arousal_in`: Degrees of physiological activation/alertness (`low`, `medium`, `high`)
- **Outputs (Consequents)** [0.0 - 1.0]:
  - `valence_out`: Target track emotional positivity
  - `energy_out`: Target track energy and intensity
  - `danceability_out`: Target track rhythmicity and groove
  - `tempo_out`: Target track normalized speed

### 2. Rule Base (9 Rules)
| Input Valence | Input Arousal | Mapped Mood Profile | Target Valence | Target Energy | Target Danceability | Target Tempo |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Low** | **Low** | Sad / Lethargic | Low | Low | Low | Low |
| **Low** | **Medium** | Gloomy / Heavy | Low | Medium | Low | Medium |
| **Low** | **High** | Angry / Tense | Low | High | Medium | High |
| **Medium** | **Low** | Mellow / Nostalgic | Medium | Low | Low | Low |
| **Medium**| **Medium** | Neutral / Balanced | Medium | Medium | Medium | Medium |
| **Medium**| **High** | Alert / Driving | Medium | High | Medium | High |
| **High** | **Low** | Calm / Peaceful | High | Low | Medium | Low |
| **High** | **Medium** | Happy / Chilled | High | Medium | High | Medium |
| **High** | **High** | Excited / Joyful | High | High | High | High |

---

## 🚀 Getting Started

### Prerequisites
Make sure you have **Python 3.10+** installed on your system.

### 1. Clone & Navigate
Navigate to the project root directory:
```bash
cd /Users/anandraj/emotion-music-recommender
```

### 2. Set Up a Virtual Environment
It is highly recommended to isolate dependencies in a virtual environment:
```bash
# Create the environment
python3 -m venv .venv

# Activate the environment (macOS/Linux)
source .venv/bin/activate

# Activate the environment (Windows PowerShell)
# .venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
Install all package requirements, including `scikit-fuzzy` and its dependencies:
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the local development server:
```bash
python app.py
```

### 5. Access the Web App
Open your web browser and navigate to:
```text
http://127.0.0.1:5001
```

---

## 🧠 Match Calculation Math

For each track $i$ in the database, the engine computes a weighted Euclidean distance $d_i$ to the target feature vector:

$$d_i = \sqrt{w_v(V_t - V_i)^2 + w_e(E_t - E_i)^2 + w_d(D_t - D_i)^2 + w_{\tau}(T_t - T_i)^2}$$

Where:
- $V_t, E_t, D_t, T_t$ are the defuzzified target features.
- $V_i, E_i, D_i, T_i$ are the features of track $i$.
- $w_v = w_e = 1.2$ (primary mood markers receive higher weight).
- $w_d = w_{\tau} = 0.8$ (rhythm/speed receive standard alignment weight).

The match score is then normalized to a percentage scale:

$$\text{Match Score} = 100 \times \left(1.0 - \frac{d_i}{d_{\text{max}}}\right)$$

Tracks are sorted by match score, and the top 6 matches are recommended to the user.

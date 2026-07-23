document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const valenceSlider = document.getElementById('valenceSlider');
    const arousalSlider = document.getElementById('arousalSlider');
    const valenceVal = document.getElementById('valenceVal');
    const arousalVal = document.getElementById('arousalVal');
    const moodLabelText = document.getElementById('moodLabelText');
    const strategyCards = document.querySelectorAll('.strategy-card');
    const btnRecommend = document.getElementById('btnRecommend');
    
    // View sections
    const placeholderPanel = document.getElementById('placeholderPanel');
    const loadingPanel = document.getElementById('loadingPanel');
    const resultsContainer = document.getElementById('resultsContainer');
    const loadingStatusText = document.getElementById('loadingStatusText');
    
    // Results elements
    const recStrategyName = document.getElementById('recStrategyName');
    const recStrategyDesc = document.getElementById('recStrategyDesc');
    
    // Target feature values
    const targetValence = document.getElementById('targetValence');
    const targetValenceBar = document.getElementById('targetValenceBar');
    const targetEnergy = document.getElementById('targetEnergy');
    const targetEnergyBar = document.getElementById('targetEnergyBar');
    const targetDanceability = document.getElementById('targetDanceability');
    const targetDanceabilityBar = document.getElementById('targetDanceabilityBar');
    const targetTempo = document.getElementById('targetTempo');
    const targetTempoBar = document.getElementById('targetTempoBar');
    
    // Songs grid and plot image
    const songsGrid = document.getElementById('songsGrid');
    const fisPlotImg = document.getElementById('fisPlotImg');
    
    // Tab controls
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    let activeStrategy = 'match';
    let loadingInterval = null;

    // 1. Russell's Circumplex Model Dynamic Mood Labeling
    function getMoodLabel(valence, arousal) {
        const v = parseFloat(valence);
        const a = parseFloat(arousal);
        
        if (v < 3.5 && a < 3.5) {
            return { text: "Sad / Depressed 😢", color: "#8b5cf6" }; // Purple
        } else if (v < 3.5 && a >= 3.5 && a < 6.5) {
            return { text: "Gloomy / Bored 🌧️", color: "#3b82f6" }; // Blue
        } else if (v < 3.5 && a >= 6.5) {
            return { text: "Angry / Anxious ⚡", color: "#ef4444" }; // Red
        } else if (v >= 3.5 && v < 6.5 && a < 3.5) {
            return { text: "Tired / Sleepy 😴", color: "#9ca3af" }; // Gray
        } else if (v >= 3.5 && v < 6.5 && a >= 3.5 && a < 6.5) {
            return { text: "Neutral / Balanced 😐", color: "#f9fafb" }; // White
        } else if (v >= 3.5 && v < 6.5 && a >= 6.5) {
            return { text: "Alert / Restless 🫨", color: "#f59e0b" }; // Amber
        } else if (v >= 6.5 && a < 3.5) {
            return { text: "Calm / Peaceful 😌", color: "#10b981" }; // Emerald
        } else if (v >= 6.5 && a >= 3.5 && a < 6.5) {
            return { text: "Relaxed / Happy 😊", color: "#10b981" }; // Emerald
        } else { // v >= 6.5 && a >= 6.5
            return { text: "Excited / Joyful 🎉", color: "#ec4899" }; // Pink
        }
    }

    function updateSliderDisplays() {
        const vVal = valenceSlider.value;
        const aVal = arousalSlider.value;
        
        valenceVal.textContent = parseFloat(vVal).toFixed(1);
        arousalVal.textContent = parseFloat(aVal).toFixed(1);
        
        const labelInfo = getMoodLabel(vVal, aVal);
        moodLabelText.textContent = labelInfo.text;
        moodLabelText.style.color = labelInfo.color;
        
        // Update slider values colors
        valenceVal.style.color = labelInfo.color;
        arousalVal.style.color = labelInfo.color;
    }

    valenceSlider.addEventListener('input', updateSliderDisplays);
    arousalSlider.addEventListener('input', updateSliderDisplays);
    
    // Initialize displays
    updateSliderDisplays();

    // 2. Strategy Card Select
    strategyCards.forEach(card => {
        card.addEventListener('click', () => {
            strategyCards.forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            activeStrategy = card.getAttribute('data-strategy');
        });
    });

    // 3. Tab Switches
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
        });
    });

    // 4. Recommendation Process
    btnRecommend.addEventListener('click', async () => {
        // Toggle view states to loading
        placeholderPanel.style.display = 'none';
        resultsContainer.style.display = 'none';
        loadingPanel.style.display = 'flex';
        
        // Cycle loading messages
        const loadingMessages = [
            "Fuzzifying emotional valence...",
            "Fuzzifying energy arousal...",
            "Evaluating 9 rule-base combinations...",
            "Executing defuzzification (Centroid method)...",
            "Generating target acoustic descriptors...",
            "Performing weighted Euclidean distance search...",
            "Mapping Unsplash and custom cover art...",
            "Constructing fuzzy inference visualization plot...",
            "Assembling recommendations grid..."
        ];
        
        let messageIdx = 0;
        loadingStatusText.textContent = loadingMessages[0];
        
        if (loadingInterval) clearInterval(loadingInterval);
        loadingInterval = setInterval(() => {
            messageIdx = (messageIdx + 1) % loadingMessages.length;
            loadingStatusText.textContent = loadingMessages[messageIdx];
        }, 600);

        // Prepare request body
        const requestBody = {
            valence: parseFloat(valenceSlider.value),
            arousal: parseFloat(arousalSlider.value),
            strategy: activeStrategy
        };

        try {
            // Short artificial delay to allow animations and messages to be experienced
            await new Promise(resolve => setTimeout(resolve, 1800));

            const response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestBody)
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.error || 'Server returned an error');
            }

            const data = await response.json();
            
            // Render results
            renderResults(data);
            
        } catch (error) {
            console.error('Recommendation request failed:', error);
            alert(`Error: ${error.message}`);
            // Revert back to placeholder
            loadingPanel.style.display = 'none';
            placeholderPanel.style.display = 'flex';
        } finally {
            if (loadingInterval) {
                clearInterval(loadingInterval);
                loadingInterval = null;
            }
        }
    });

    // 5. Populate and render recommendation results
    function renderResults(data) {
        // Switch view states
        loadingPanel.style.display = 'none';
        resultsContainer.style.display = 'block';
        
        // Populate strategy details
        recStrategyName.textContent = data.strategy.name;
        recStrategyDesc.textContent = data.strategy.description;
        
        // Populate target audio features numerical values and bar fills
        targetValence.textContent = data.target_features.valence.toFixed(2);
        targetValenceBar.style.width = `${data.target_features.valence * 100}%`;
        
        targetEnergy.textContent = data.target_features.energy.toFixed(2);
        targetEnergyBar.style.width = `${data.target_features.energy * 100}%`;
        
        targetDanceability.textContent = data.target_features.danceability.toFixed(2);
        targetDanceabilityBar.style.width = `${data.target_features.danceability * 100}%`;
        
        targetTempo.textContent = data.target_features.tempo.toFixed(2);
        targetTempoBar.style.width = `${data.target_features.tempo * 100}%`;
        
        // Render Matplotlib Plot
        fisPlotImg.src = `data:image/png;base64,${data.plot_image}`;
        
        // Clear previous recommendations
        songsGrid.innerHTML = '';
        
        // Loop and add songs in dynamic cards
        data.recommendations.forEach(song => {
            const songCard = document.createElement('div');
            songCard.className = 'song-card';
            
            // Build absolute YouTube search link
            // Format: https://www.youtube.com/results?search_query=Song+Artist
            const ytQuery = encodeURIComponent(`${song.title} ${song.artist}`);
            const ytSearchUrl = `https://www.youtube.com/results?search_query=${ytQuery}`;

            songCard.innerHTML = `
                <div class="song-image-container">
                    <img class="song-cover-img" src="${song.cover_url}" alt="${song.title} album art" loading="lazy">
                    <span class="song-badge-genre">${song.genre}</span>
                    <span class="song-badge-match">${song.match_score}%</span>
                </div>
                <div class="song-body">
                    <div class="song-meta">
                        <div class="song-title-row">
                            <h4 class="song-card-title" title="${song.title}">${song.title}</h4>
                        </div>
                        <div class="song-card-artist" title="${song.artist}">${song.artist}</div>
                    </div>
                    
                    <p class="song-card-desc" title="${song.description}">${song.description}</p>
                    
                    <div class="song-meters">
                        <div class="song-meter-row">
                            <div class="song-meter-label-row">
                                <span>Valence</span>
                                <span style="font-family: var(--font-mono);">${song.valence.toFixed(2)}</span>
                            </div>
                            <div class="song-meter-bar-bg">
                                <div class="song-meter-bar-fill" style="width: ${song.valence * 100}%; background: var(--secondary-gradient)"></div>
                            </div>
                        </div>
                        <div class="song-meter-row">
                            <div class="song-meter-label-row">
                                <span>Energy</span>
                                <span style="font-family: var(--font-mono);">${song.energy.toFixed(2)}</span>
                            </div>
                            <div class="song-meter-bar-bg">
                                <div class="song-meter-bar-fill" style="width: ${song.energy * 100}%; background: var(--primary-gradient)"></div>
                            </div>
                        </div>
                    </div>
                    
                    <div class="song-actions">
                        <a href="${song.url}" target="_blank" class="btn-play-spotify" title="Listen on Spotify">
                            <i class="fab fa-spotify"></i>
                        </a>
                        <a href="${ytSearchUrl}" target="_blank" class="btn-play-youtube" title="Search and Play on YouTube">
                            <i class="fab fa-youtube"></i>
                            Play on YouTube
                        </a>
                    </div>
                </div>
            `;
            songsGrid.appendChild(songCard);
        });

        // Clean scrolling transition down to the generated results header
        const scrollTarget = document.getElementById('resultsHeader');
        if (scrollTarget) {
            scrollTarget.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }
});

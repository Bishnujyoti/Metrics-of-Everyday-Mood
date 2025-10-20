import streamlit as st
from textblob import TextBlob
import pandas as pd
import plotly.express as px
from datetime import datetime
import json, os, random
from transformers import pipeline
from streamlit_lottie import st_lottie

# Load Lottie Animation 🐶 (local file)
with open("dog.json", "r") as f:
    dog_animation = json.load(f)

# Load Sentiment Model
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

sentiment_model = load_model()

# Sentiment Function
def get_sentiment(text):
    result = sentiment_model(text)[0]
    label = result['label']
    if label == "LABEL_2":  # Positive = return Happy 
        return "Happy 😊"
    elif label == "LABEL_0":  # Negative = return Sad
        return "Sad 😢"
    else:
        return "Neutral 😐" # Neutral = return zero

# Config & Files
st.set_page_config(page_title="Mood Metrics", page_icon="😊", layout="wide")
SENTIMENT_FILE = "sentiment_data.json"

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

def load_sentiment_data():
    if os.path.exists(SENTIMENT_FILE):
        with open(SENTIMENT_FILE, "r") as f:
            return json.load(f)
    else:
        return {}

def save_sentiment_data(data):
    with open(SENTIMENT_FILE, "w") as f:
        json.dump(data, f)

sentiment_records = load_sentiment_data()

if "selected_date" not in st.session_state:
    st.session_state["selected_date"] = str(datetime.today().date())

if str(st.session_state["selected_date"]) not in sentiment_records:
    sentiment_records[str(st.session_state["selected_date"])] = {"Happy 😊": 0, "Sad 😢": 0, "Neutral 😐": 0}

# Themes
def toggle_theme():
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"

if st.session_state["theme"] == "dark":
    background_color = "#1E1E1E"
    text_color = "#FFFFFF"
    secondary_background_color = "#252525"
    button_color = "background: linear-gradient(to right, #ff7e5f, #feb47b); color: white;"
else:
    background_color = "#FFFFFF"
    text_color = "#000000"
    secondary_background_color = "#F0f0f0"
    button_color = "background: linear-gradient(to right, #4facfe, #00f2fe); color: black;"

# Styling
st.markdown(f"""
    <style>
        body {{
            background-color: {background_color};
            color: {text_color};
        }}
        .stButton>button {{
            {button_color}
            border: none;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-size: 1rem;
            font-weight: bold;
        }}
        .sentiment-result {{
            font-size: 2rem;
            font-weight: bold;
            color: {text_color};
            text-align: center;
        }}
    </style>
""", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2 = st.tabs(["🏠 Home", "💞 Data Donation"])

# HOME TAB
with tab1:
    st.markdown(f"<h1 style='text-align: center;'>Mood Metrics</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>✨ Turning your feelings into insights ✨</h3>", unsafe_allow_html=True)

    st.button("Toggle Theme", on_click=toggle_theme)
    
    selected_date = st.date_input("Select Date", min_value=datetime(2025, 1, 1), max_value=datetime.today())
    st.session_state["selected_date"] = str(selected_date)
    
    if str(selected_date) not in sentiment_records:
        sentiment_records[str(selected_date)] = {"Happy 😊": 0, "Sad 😢": 0, "Neutral 😐": 0}
    
    save_sentiment_data(sentiment_records)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Enter Text Below:")
        input_text = st.text_area("", height=150)
        
        if st.button("Analyze Sentiment"):
            if input_text:
                sentiment = get_sentiment(input_text)
                sentiment_records[str(selected_date)][sentiment] += 1
                save_sentiment_data(sentiment_records)
                st.markdown(f"<div class='sentiment-result'>Sentiment: {sentiment}</div>", unsafe_allow_html=True)
            else:
                st.warning("Please enter some text.")
    
    with col2:
        st.markdown("### Mood Chart")
        mood_data = pd.DataFrame({
            "Mood": list(sentiment_records[str(selected_date)].keys()),
            "Count": list(sentiment_records[str(selected_date)].values()),
        })
        fig = px.bar(
            mood_data,
            x="Mood",
            y="Count",
            title="Mood Sentiment Count",
            color="Mood",
            color_discrete_map={
                "Happy 😊": "lightgreen",
                "Sad 😢": "lightcoral",
                "Neutral 😐": "lightskyblue",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

    # 🐶 Mood Booster Section
    st.markdown("### 🌸 Mood Booster")
    st_lottie(dog_animation, height=180, key="dog")

    if st.button("🐾 Cheer Me Up!"):
        messages = [
            "You're doing amazing, even if you don't see it yet 💪",
            "Drink some water, your brain will thank you 💧",
            "You’re the main character today 🎬",
            "A dog once said: 'Woof... which means you're awesome' 🐶",
            "Your smile is literally software update for my soul 😄",
            "You survived 100% of your bad days so far 💖",
            "Plot twist: you’re actually doing great 😌"
        ]
        st.success(random.choice(messages))

    # Daily Summary
    st.markdown("### Record Your Sentiment for the Day")
    if str(selected_date) in sentiment_records:
        sentiment_counts = sentiment_records[str(selected_date)]
        total_sentiments = sum(sentiment_counts.values())
        
        if total_sentiments > 0:
            happy_percentage = (sentiment_counts["Happy 😊"] / total_sentiments) * 100
            sad_percentage = (sentiment_counts["Sad 😢"] / total_sentiments) * 100
            neutral_percentage = (sentiment_counts["Neutral 😐"] / total_sentiments) * 100
            
            if happy_percentage > sad_percentage and happy_percentage > neutral_percentage:
                sentiment_on_date = "Happy 😊"
            elif sad_percentage > happy_percentage and sad_percentage > neutral_percentage:
                sentiment_on_date = "Sad 😢"
            else:
                sentiment_on_date = "Neutral 😐"
            
            st.success(f"Your average sentiment for {selected_date} is {sentiment_on_date}.")
        else:
            st.warning("No data available for the selected date.")

# DATA DONATION TAB
with tab2:
    st.markdown("<h2 style='text-align:center;'>💞 Data Donation</h2>", unsafe_allow_html=True)
    st.warning("⚠️ Entries submitted here may be read by developers to improve the model, "
               "but they will remain **strictly confidential** and **never shared publicly**.")
    
    donated_text = st.text_area("Share your mood entry to help improve Mood Metrics (optional):", height=200)
    if st.button("Donate My Entry"):
        if donated_text.strip():
            with open("donated_entries.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} — {donated_text}\n")
            st.success("💖 Thank you for your contribution! You're helping make mood tracking smarter and kinder.")
        else:
            st.warning("Please write something before donating.")

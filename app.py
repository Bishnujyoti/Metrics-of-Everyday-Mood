import streamlit as st
from transformers import pipeline
from streamlit_lottie import st_lottie
import pandas as pd
import plotly.express as px
from datetime import datetime
import json, random, os

# --------------------------
# Load Dog Animation (local)
# --------------------------
with open("dog.json", "r") as f:
    dog_animation = json.load(f)

# --------------------------
# Load Sentiment Model (Roberta)
# --------------------------
@st.cache_resource
def load_model():
    return pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

sentiment_model = load_model()

# --------------------------
# Sentiment Function
# --------------------------
def get_sentiment(text):
    result = sentiment_model(text)[0]
    label = result['label']
    if label == "LABEL_2":  # Positive
        return "Happy 😊"
    elif label == "LABEL_0":  # Negative
        return "Sad 😢"
    else:
        return "Neutral 😐"

# --------------------------
# Streamlit Config
# --------------------------
st.set_page_config(page_title="Mood Metrics", page_icon="😊", layout="wide")

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

if "sentiment_data" not in st.session_state:
    st.session_state["sentiment_data"] = {}

# --------------------------
# Theme Toggle
# --------------------------
def toggle_theme():
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"

# --------------------------
# Apply Styling
# --------------------------
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

# --------------------------
# Tabs
# --------------------------
tab1, tab2 = st.tabs(["🏠 Home", "💞 Data Donation"])

# --------------------------
# HOME TAB
# --------------------------
with tab1:
    st.markdown(f"<h1 style='text-align: center;'>Mood Metrics</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='text-align: center;'>✨ Turning your feelings into insights ✨</h3>", unsafe_allow_html=True)

    st.button("Toggle Theme", on_click=toggle_theme)

    # Select Date
    selected_date = st.date_input("Select Date", min_value=datetime(2025, 1, 1), max_value=datetime.today())
    date_str = str(selected_date)

    if date_str not in st.session_state["sentiment_data"]:
        st.session_state["sentiment_data"][date_str] = {"Happy 😊": 0, "Sad 😢": 0, "Neutral 😐": 0}

    # Input & Sentiment
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Enter Text Below:")
        input_text = st.text_area("", height=150)

        if st.button("Analyze Sentiment"):
            if input_text.strip():
                sentiment = get_sentiment(input_text)
                st.session_state["sentiment_data"][date_str][sentiment] += 1
                st.markdown(f"<div class='sentiment-result'>Sentiment: {sentiment}</div>", unsafe_allow_html=True)
            else:
                st.warning("Please enter some text.")

    with col2:
        st.markdown("### Mood Chart")
        data = st.session_state["sentiment_data"][date_str]
        mood_data = pd.DataFrame({"Mood": list(data.keys()), "Count": list(data.values())})
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

    # 🐶 Mood Booster
    st.markdown("### 🐾 Mood Booster")
    st_lottie(dog_animation, height=180, key="dog")

    if st.button("💖 Cheer Me Up!"):
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

    # Summary
    st.markdown("### Record Your Sentiment for the Day")
    data = st.session_state["sentiment_data"][date_str]
    total = sum(data.values())
    if total > 0:
        happy, sad, neutral = data["Happy 😊"], data["Sad 😢"], data["Neutral 😐"]
        dominant = max(data, key=data.get)
        st.success(f"Your average sentiment for {date_str} is {dominant}.")
    else:
        st.warning("No data available for the selected date.")

    # Data Controls
    st.markdown("### 📦 Manage Your Mood Data")
    colA, colB = st.columns(2)
    with colA:
        if st.button("💾 Download My Data"):
            json_data = json.dumps(st.session_state["sentiment_data"], indent=4)
            st.download_button("Click to Download", data=json_data, file_name="my_mood_data.json", mime="application/json")

    with colB:
        uploaded_file = st.file_uploader("Upload Your Mood Data (JSON)", type=["json"])
        if uploaded_file:
            uploaded_data = json.load(uploaded_file)
            st.session_state["sentiment_data"].update(uploaded_data)
            st.success("✅ Data imported successfully!")

# --------------------------
# DATA DONATION TAB
# --------------------------
with tab2:
    st.markdown("<h2 style='text-align:center;'>💞 Data Donation</h2>", unsafe_allow_html=True)
    st.warning("⚠️ Entries here may be **read by developers** to improve the model, "
               "but will remain **strictly confidential** and **never shared publicly.**")

    donated_text = st.text_area("Share your mood entry to help improve Mood Metrics (optional):", height=200)
    if st.button("Donate My Entry"):
        if donated_text.strip():
            with open("donated_entries.txt", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()} — {donated_text}\n")
            st.success("💖 Thank you for your contribution! You're helping make mood tracking smarter and kinder.")
        else:
            st.warning("Please write something before donating.")

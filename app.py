import streamlit as st    
from textblob import TextBlob
import pandas as pd
import plotly.express as px
from datetime import datetime
import json
import os

def get_sentiment(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity

    if sentiment > 0:
        return "Happy 😊"
    elif sentiment < 0:
        return "Sad 😢"
    else:
        return "Neutral 😐"

st.set_page_config(page_title="Sentiment Analysis App", page_icon="😊", layout="wide")

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

def toggle_theme():
    st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"

def clear_input():
    st.session_state["input_text"] = ""

if st.session_state["theme"] == "dark":
    background_color = "#1E1E1E"
    text_color = "#FFFFFF"
    font_color = "#FFFFFF"
    secondary_background_color = "#252525"
    axis_label_color = "#ffffff"  # Default axis label color (dark theme)
    title_color = "#ffffff"  # Default title color (dark theme)
    legend_label_color = "#ffffff"
    button_color = "background: linear-gradient(to right, #ff7e5f, #feb47b); color: white;"
else:
    background_color = "#FFFFFF"
    text_color = "#000000"
    font_color = "#000000"
    secondary_background_color = "#F0f0f0"
    axis_label_color = "#000000"  # Default axis label color (dark theme)
    title_color = "#000000"  # Default title color (dark theme)
    legend_label_color = "#000000"  
    button_color = "background: linear-gradient(to right, #4facfe, #00f2fe); color: black;"

st.markdown(f"""
    <style>
        body {{
            background-color: {background_color};
            color: {font_color};
        }}
        .stTextArea textarea {{
            background-color: {secondary_background_color};
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
        .stButton>button:hover {{
            filter: brightness(1.2);
        }}
        .sentiment-result {{
            font-size: 2rem;
            font-weight: bold;
            color: {text_color};
            text-align: center;
        }}
    </style>
""", unsafe_allow_html=True)

st.markdown(f"<h1 style='text-align: center;'>Mood Metrics</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>✨Turning your feelings into insights.✨</h3>", unsafe_allow_html=True)

st.button("Toggle Theme", on_click=toggle_theme)

st.button("Clear Input", on_click=clear_input)

selected_date = st.date_input("Select Date", min_value=datetime(2025, 1, 1), max_value=datetime.today())

st.session_state["selected_date"] = str(selected_date)

if str(selected_date) not in sentiment_records:
    sentiment_records[str(selected_date)] = {"Happy 😊": 0, "Sad 😢": 0, "Neutral 😐": 0}

save_sentiment_data(sentiment_records)

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Enter Text Below:")
    input_text = st.text_area("", height=150)

    
    button = st.button("Analyze Sentiment")

    if button:
        if input_text:
            sentiment = get_sentiment(input_text)
            
            sentiment_records[str(selected_date)][sentiment] += 1
            
            save_sentiment_data(sentiment_records)
            
            st.markdown(f"<div class='sentiment-result'>Sentiment: {sentiment}</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter some text.")

with col2:
    st.markdown("### Mood Chart")
    
    
    mood_data = pd.DataFrame(
        {
            "Mood": list(sentiment_records[str(selected_date)].keys()),
            "Count": list(sentiment_records[str(selected_date)].values()),
        }
    )

   
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
    fig.update_layout(
        plot_bgcolor=background_color,
        paper_bgcolor=background_color,
        font_color=font_color,
        title=dict(text="Mood Sentiment Count", font=dict(color=title_color)),
        xaxis=dict(
        color=axis_label_color,
        title_font=dict(color=axis_label_color),
        tickfont=dict(color=axis_label_color)
    ),
    yaxis=dict(
        color=axis_label_color,
        title_font=dict(color=axis_label_color),
        tickfont=dict(color=axis_label_color)
    ),
    legend=dict(
        font=dict(color=legend_label_color)
    ),
    )
    st.plotly_chart(fig, use_container_width=True)

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







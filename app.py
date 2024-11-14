import pandas as pd
import numpy as np
from flask import Flask, request, jsonify
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from textstat import flesch_reading_ease
from scipy.sparse import hstack
import re
import string
import os

# Initialize the Flask app
app = Flask(__name__)

# Load model and resources
model = None
vectorizer = None
sid = None

def load_and_train_model():
    global model, vectorizer, sid

    # Load dataset
    news = pd.read_csv('fakeandTrue_news_dataset')
    news = news.drop_duplicates()
    news = news.dropna(subset=['title', 'text'])

    # Clean text function
    def clean_text(text):
        return re.sub(f"[{re.escape(string.punctuation)}]", '', text.lower())
    
    news['text'] = news['text'].astype(str).apply(clean_text)
    
    # Sentiment and readability scores
    nltk.download('vader_lexicon')
    sid = SentimentIntensityAnalyzer()
    news['sentiment_score'] = news['text'].apply(lambda x: sid.polarity_scores(x)['compound'])
    news['readability_score'] = news['text'].apply(lambda x: flesch_reading_ease(x))

    # Vectorize the text
    vectorizer = TfidfVectorizer()
    tfidf_text = vectorizer.fit_transform(news['text'])

    # Combine tfidf with other features
    x = hstack((tfidf_text, news[['sentiment_score', 'readability_score']].values))
    y = news['label']

    # Train-test split
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

    # Train logistic regression model
    model = LogisticRegression(max_iter=1000)  # Increased iterations for convergence
    model.fit(x_train, y_train)

    # Model accuracy
    y_pred = model.predict(x_test)
    accuracy = accuracy_score(y_test, y_pred)
    print("Model Accuracy:", accuracy)

# Load model and resources at startup
load_and_train_model()

# Prediction endpoint
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')

    # Clean and process input text
    text_cleaned = re.sub(f"[{re.escape(string.punctuation)}]", '', text.lower())
    tfidf_text = vectorizer.transform([text_cleaned])
    
    # Calculate sentiment and readability scores
    sentiment_score = sid.polarity_scores(text_cleaned)['compound']
    readability_score = flesch_reading_ease(text_cleaned)

    # Combine all features
    features = hstack((tfidf_text, [[sentiment_score, readability_score]]))

    # Make prediction
    prediction = model.predict(features)

    # Return prediction result
    result = "real" if prediction[0] == 1 else "fake"
    return jsonify({'prediction': result})

# Run the app
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Default to 5000 if not specified
    app.run(host='0.0.0.0', port=port)  # Bind to all interfaces

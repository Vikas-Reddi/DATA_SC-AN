# Use a minimal Python 3.9 image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only requirements to leverage Docker cache more efficiently
COPY requirements.txt .

# Install necessary system dependencies
RUN apt-get update && apt-get install -y \
       gcc \
       build-essential \
       && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY . .

# Download the NLTK lexicon for sentiment analysis
RUN python -m nltk.downloader vader_lexicon

EXPOSE 5000

# Environment variables for Flask
ENV FLASK_ENV=production


# Use Waitress as the application server with Flask app, binding to Render's $PORT environment variable
CMD ["waitress-serve", "--port=${PORT}", "app:app"]

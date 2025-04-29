import tweepy
from transformers import pipeline
import pandas as pd
import time

# Twitter API credentials (replace with your own)
api_key = "your_api_key"
api_secret = "your_api_secret"
access_token = "your_access_token"
access_token_secret = "your_access_token_secret"

# Authenticate with Twitter API
auth = tweepy.OAuthHandler(api_key, api_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)

# Initialize the sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment")

# Keyword or hashtag to search for
search_query = "#AIinAfrica"  # Replace with your desired keyword or hashtag
num_tweets = 50  # Number of tweets to scrape (adjust for learning purposes)

# List to store tweet data and sentiment
results = []

# Scrape tweets
print(f"Scraping {num_tweets} tweets for {search_query}...")
for tweet in tweepy.Cursor(api.search_tweets, q=search_query, lang="en", tweet_mode="extended").items(num_tweets):
    try:
        # Extract tweet text (handle retweets)
        if hasattr(tweet, "retweeted_status"):
            tweet_text = tweet.retweeted_status.full_text
        else:
            tweet_text = tweet.full_text

        # Clean the tweet text (remove URLs, mentions, etc.)
        tweet_text_cleaned = " ".join(word for word in tweet_text.split() if not (word.startswith("http") or word.startswith("@")))

        # Perform sentiment analysis
        sentiment_result = sentiment_analyzer(tweet_text_cleaned[:280])[0]  # Truncate to 280 chars for model compatibility
        sentiment_label = sentiment_result["label"]
        sentiment_score = sentiment_result["score"]

        # Map the model's labels to readable sentiment (LABEL_0: negative, LABEL_1: neutral, LABEL_2: positive)
        sentiment_map = {"LABEL_0": "negative", "LABEL_1": "neutral", "LABEL_2": "positive"}
        sentiment = sentiment_map[sentiment_label]

        # Store the results
        results.append({
            "Tweet": tweet_text,
            "Sentiment": sentiment,
            "Confidence": sentiment_score,
            "User": tweet.user.screen_name,
            "Created_At": tweet.created_at
        })

        print(f"Processed tweet: {tweet_text[:50]}... | Sentiment: {sentiment}")
        
        # Add a delay to avoid rate limiting
        time.sleep(1)

    except Exception as e:
        print(f"Error processing tweet: {e}")
        continue

# Save results to CSV
if results:
    df = pd.DataFrame(results)
    df.to_csv("twitter_sentiment_analysis.csv", index=False)
    print(f"Saved {len(results)} tweets with sentiment analysis to twitter_sentiment_analysis.csv")
else:
    print("No tweets found or processed.")

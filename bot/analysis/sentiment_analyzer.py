import requests
import json
from textblob import TextBlob
from datetime import datetime, timedelta

class SentimentAnalyzer:
    def __init__(self, config):
        self.config = config
        self.news_api_key = config.get('NEWS_API_KEY')
        self.twitter_bearer_token = config.get('TWITTER_BEARER_TOKEN')
        
    def get_market_sentiment(self, symbol='EURUSD'):
        """Analyze market sentiment from news and social media"""
        news_sentiment = self._analyze_news_sentiment(symbol)
        twitter_sentiment = self._analyze_twitter_sentiment(symbol)
        
        # Combine sentiment scores
        total_samples = news_sentiment['sample_size'] + twitter_sentiment['sample_size']
        if total_samples > 0:
            combined_score = (
                news_sentiment['score'] * news_sentiment['sample_size'] +
                twitter_sentiment['score'] * twitter_sentiment['sample_size']
            ) / total_samples
        else:
            combined_score = 0
            
        return {
            'combined_sentiment': combined_score,
            'news_sentiment': news_sentiment,
            'twitter_sentiment': twitter_sentiment,
            'interpretation': self._interpret_sentiment(combined_score)
        }
        
    def _analyze_news_sentiment(self, symbol):
        """Analyze sentiment from financial news"""
        if not self.news_api_key:
            return {'score': 0, 'sample_size': 0}
            
        try:
            # Get news articles
            url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={self.news_api_key}"
            response = requests.get(url)
            articles = response.json().get('articles', [])
            
            # Analyze sentiment
            scores = []
            for article in articles[:10]:  # Limit to 10 articles
                analysis = TextBlob(article['title'] + ' ' + article['description'])
                scores.append(analysis.sentiment.polarity)
                
            if scores:
                avg_score = sum(scores) / len(scores)
                return {'score': avg_score, 'sample_size': len(scores)}
                
        except Exception as e:
            pass
            
        return {'score': 0, 'sample_size': 0}
        
    def _analyze_twitter_sentiment(self, symbol):
        """Analyze sentiment from Twitter"""
        if not self.twitter_bearer_token:
            return {'score': 0, 'sample_size': 0}
            
        try:
            # Get recent tweets (simplified - in reality you'd use Twitter API)
            headers = {"Authorization": f"Bearer {self.twitter_bearer_token}"}
            params = {
                'query': f'#{symbol} lang:en',
                'max_results': 50,
                'tweet.fields': 'created_at'
            }
            response = requests.get(
                "https://api.twitter.com/2/tweets/search/recent",
                headers=headers,
                params=params
            )
            tweets = response.json().get('data', [])
            
            # Analyze sentiment
            scores = []
            for tweet in tweets:
                analysis = TextBlob(tweet['text'])
                scores.append(analysis.sentiment.polarity)
                
            if scores:
                avg_score = sum(scores) / len(scores)
                return {'score': avg_score, 'sample_size': len(scores)}
                
        except Exception as e:
            pass
            
        return {'score': 0, 'sample_size': 0}
        
    def _interpret_sentiment(self, score):
        """Interpret sentiment score"""
        if score > 0.2:
            return 'Strongly Positive'
        elif score > 0.05:
            return 'Positive'
        elif score < -0.2:
            return 'Strongly Negative'
        elif score < -0.05:
            return 'Negative'
        else:
            return 'Neutral'
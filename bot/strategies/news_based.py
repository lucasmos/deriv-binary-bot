import requests
from textblob import TextBlob
from datetime import datetime, timedelta
from .base_strategy import BaseStrategy

class NewsBasedStrategy(BaseStrategy):
    def __init__(self, config=None):
        super().__init__(config)
        self.news_api_key = config.get('NEWS_API_KEY')
        self.min_sentiment = config.get('min_sentiment', 0.3)
        self.max_age_hours = config.get('max_age_hours', 6)
        
    def analyze(self, data):
        """Analyze news sentiment for trading signals"""
        if not self.news_api_key:
            return None
            
        # Get recent news articles
        news = self._get_relevant_news(data['symbol'] if isinstance(data, dict) else 'EURUSD')
        
        if not news:
            return None
            
        # Calculate average sentiment
        sentiment = sum(article['sentiment'] for article in news) / len(news)
        
        # Generate signals based on sentiment
        if sentiment >= self.min_sentiment:
            return {'direction': 'buy', 'confidence': min(0.9, sentiment), 'type': 'news'}
        elif sentiment <= -self.min_sentiment:
            return {'direction': 'sell', 'confidence': min(0.9, -sentiment), 'type': 'news'}
            
        return None
        
    def _get_relevant_news(self, symbol):
        """Fetch and analyze recent news articles"""
        try:
            url = f"https://newsapi.org/v2/everything?q={symbol}&apiKey={self.news_api_key}"
            response = requests.get(url)
            articles = response.json().get('articles', [])
            
            relevant_news = []
            for article in articles:
                published_at = datetime.strptime(article['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
                if (datetime.utcnow() - published_at) > timedelta(hours=self.max_age_hours):
                    continue
                    
                text = f"{article['title']}. {article['description']}"
                analysis = TextBlob(text)
                sentiment = analysis.sentiment.polarity
                
                relevant_news.append({
                    'title': article['title'],
                    'sentiment': sentiment,
                    'time': published_at
                })
                
            return relevant_news
            
        except Exception as e:
            return None
            
    def get_parameters(self):
        return {
            'min_sentiment': self.min_sentiment,
            'max_age_hours': self.max_age_hours,
            'strategy_type': 'news_based'
        }
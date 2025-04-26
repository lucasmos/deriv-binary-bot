import json
import os
from datetime import datetime, timedelta

class Cache:
    def __init__(self, config):
        self.config = config
        self.cache_dir = config.get('CACHE_DIR', 'data/cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        
    def get(self, key, default=None, max_age_seconds=None):
        """Get cached value by key"""
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        
        if not os.path.exists(filepath):
            return default
            
        try:
            with open(filepath, 'r') as f:
                data = json.load(f)
                
            # Check expiration
            if max_age_seconds and 'timestamp' in data:
                cache_time = datetime.fromisoformat(data['timestamp'])
                if (datetime.utcnow() - cache_time) > timedelta(seconds=max_age_seconds):
                    return default
                    
            return data.get('value', default)
            
        except Exception:
            return default
            
    def set(self, key, value, ttl=None):
        """Set cached value with optional time-to-live"""
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        data = {
            'value': value,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if ttl:
            data['expires_at'] = (datetime.utcnow() + timedelta(seconds=ttl)).isoformat()
            
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f)
            return True
        except Exception:
            return False
            
    def delete(self, key):
        """Delete cached value"""
        filepath = os.path.join(self.cache_dir, f"{key}.json")
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False
            
    def clear_expired(self):
        """Clear all expired cache entries"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.cache_dir, filename)
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                        
                    if 'expires_at' in data:
                        expires_at = datetime.fromisoformat(data['expires_at'])
                        if datetime.utcnow() > expires_at:
                            os.remove(filepath)
                except Exception:
                    continue
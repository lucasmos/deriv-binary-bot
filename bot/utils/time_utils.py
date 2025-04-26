from datetime import datetime, timedelta
import pytz

class TimeUtils:
    @staticmethod
    def get_current_time(timezone='UTC'):
        """Get current time in specified timezone"""
        return datetime.now(pytz.timezone(timezone))
        
    @staticmethod
    def convert_timezone(dt, from_tz, to_tz):
        """Convert datetime between timezones"""
        from_zone = pytz.timezone(from_tz)
        to_zone = pytz.timezone(to_tz)
        localized = from_zone.localize(dt)
        return localized.astimezone(to_zone)
        
    @staticmethod
    def is_market_open(symbol, current_time=None):
        """Check if market is open for given symbol"""
        market_hours = {
            'EURUSD': ('08:00', '17:00', 'EST'),
            'GBPUSD': ('08:00', '17:00', 'EST'),
            'USDJPY': ('19:00', '04:00', 'EST'),
            'XAUUSD': ('18:00', '17:00', 'EST')  # Gold (24h with 1h break)
        }
        
        if symbol not in market_hours:
            return True  # Assume open if we don't have specific hours
            
        current_time = current_time or TimeUtils.get_current_time()
        open_time, close_time, tz = market_hours[symbol]
        
        # Convert to target timezone
        current_time = current_time.astimezone(pytz.timezone(tz))
        
        # Handle overnight sessions
        if close_time < open_time:  # Market closes next day
            market_open = current_time.time() >= datetime.strptime(open_time, '%H:%M').time() or \
                         current_time.time() <= datetime.strptime(close_time, '%H:%M').time()
        else:
            market_open = (current_time.time() >= datetime.strptime(open_time, '%H:%M').time() and 
                          current_time.time() <= datetime.strptime(close_time, '%H:%M').time())
            
        # Check if it's a weekday
        return market_open and current_time.weekday() < 5
        
    @staticmethod
    def time_until_next_bar(timeframe, timezone='UTC'):
        """Calculate time remaining until next candle closes"""
        now = TimeUtils.get_current_time(timezone)
        minutes = int(timeframe[:-1]) if 'm' in timeframe else 60
        
        if 'm' in timeframe:
            next_close = now.replace(second=0, microsecond=0) + \
                        timedelta(minutes=minutes - (now.minute % minutes))
        elif 'H' in timeframe:
            next_close = now.replace(minute=0, second=0, microsecond=0) + \
                        timedelta(hours=int(timeframe[:-1]))
        else:  # Daily
            next_close = now.replace(hour=0, minute=0, second=0, microsecond=0) + \
                        timedelta(days=1)
                        
        return next_close - now
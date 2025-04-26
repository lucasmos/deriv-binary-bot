import logging
import traceback
from datetime import datetime
from ..models import db, ErrorLog

class ErrorHandler:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def log_error(self, error, context=None):
        """Log an error with optional context"""
        error_msg = {
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(error),
            'type': type(error).__name__,
            'traceback': traceback.format_exc(),
            'context': context
        }
        
        # Log to console/file
        self.logger.error(error_msg)
        
        # Log to database if available
        try:
            error_log = ErrorLog(
                error_type=type(error).__name__,
                message=str(error),
                traceback=traceback.format_exc(),
                context=str(context),
                timestamp=datetime.utcnow()
            )
            db.session.add(error_log)
            db.session.commit()
        except Exception as db_error:
            self.logger.error(f"Failed to log error to database: {db_error}")
            
    def handle_api_error(self, response):
        """Handle API response errors"""
        if response.status_code >= 400:
            error_msg = f"API Error {response.status_code}: {response.text}"
            self.log_error(error_msg)
            raise Exception(error_msg)
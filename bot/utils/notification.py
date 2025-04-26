import smtplib
from email.mime.text import MIMEText
from datetime import datetime

class Notification:
    def __init__(self, config):
        self.config = config
        self.smtp_config = config.get('SMTP', {})
        
    def send_email(self, to, subject, body):
        """Send email notification"""
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = self.smtp_config.get('FROM_EMAIL')
            msg['To'] = to
            
            with smtplib.SMTP(
                self.smtp_config.get('HOST'),
                self.smtp_config.get('PORT', 587)
            ) as server:
                server.starttls()
                server.login(
                    self.smtp_config.get('USERNAME'),
                    self.smtp_config.get('PASSWORD')
                )
                server.send_message(msg)
            return True
        except Exception as e:
            return False
            
    def send_trade_alert(self, trade_details):
        """Send trade execution alert"""
        subject = f"Trade Executed: {trade_details['symbol']} {trade_details['direction']}"
        body = f"""
        Trade Details:
        - Symbol: {trade_details['symbol']}
        - Direction: {trade_details['direction']}
        - Amount: {trade_details['amount']}
        - Time: {trade_details['timestamp']}
        - Strategy: {trade_details.get('strategy', 'N/A')}
        """
        
        if self.config.get('TRADE_NOTIFICATIONS', False):
            return self.send_email(
                self.config.get('NOTIFICATION_EMAIL'),
                subject,
                body
            )
        return False
        
    def send_error_alert(self, error_details):
        """Send error notification"""
        subject = "Trading Bot Error Alert"
        body = f"""
        An error occurred in the trading bot:
        
        Error: {error_details.get('error', 'Unknown')}
        Type: {error_details.get('type', 'Unknown')}
        Time: {error_details.get('timestamp', 'Unknown')}
        
        Traceback:
        {error_details.get('traceback', 'Not available')}
        """
        
        if self.config.get('ERROR_NOTIFICATIONS', False):
            return self.send_email(
                self.config.get('ADMIN_EMAIL'),
                subject,
                body
            )
        return False
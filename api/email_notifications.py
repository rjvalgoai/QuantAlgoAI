import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
from core.logger import logger

load_dotenv()

class EmailNotifier:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.sender_email = os.getenv('SENDER_EMAIL')
        self.sender_password = os.getenv('SENDER_PASSWORD')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL')

    def send_trade_notification(self, trade_data):
        subject = f"Trade Alert: {trade_data['order_type']} {trade_data['symbol']}"
        
        body = f"""
        Trade Details:
        --------------
        Symbol: {trade_data['symbol']}
        Type: {trade_data['order_type']}
        Quantity: {trade_data['quantity']}
        Price: {trade_data['price']}
        Time: {trade_data['timestamp']}
        
        P&L: {trade_data.get('realized_pnl', 'N/A')}
        Strategy Confidence: {trade_data.get('confidence_score', 'N/A')}
        
        Risk Management:
        ---------------
        Stop Loss: {trade_data.get('stop_loss', 'N/A')}
        Take Profit: {trade_data.get('take_profit', 'N/A')}
        """
        
        try:
            self._send_email(subject, body)
            logger.info(f"Trade notification email sent successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

    def send_alert(self, alert_type, message):
        subject = f"Trading Alert: {alert_type}"
        try:
            self._send_email(subject, message)
            logger.info(f"Alert email sent successfully: {alert_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
            return False

    def _send_email(self, subject, body):
        msg = MIMEMultipart()
        msg['From'] = self.sender_email
        msg['To'] = self.recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            server.send_message(msg)

# Example Usage
if __name__ == "__main__":
    notifier = EmailNotifier()
    notifier.send_trade_notification({"order_type": "Buy", "symbol": "AAPL", "quantity": 100, "price": 150.75, "timestamp": "2023-04-15 10:30:00"})

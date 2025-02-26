import logging
from config import settings
from typing import Dict, List, Optional
import smtplib
from telegram import Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from email.mime.text import MIMEText
from telegram.error import InvalidToken

logger = logging.getLogger(__name__)

class NotificationManager:
    def __init__(self):
        self.telegram_bot = None
        self.email_server = None
        self.subscribers: List[Dict] = []
        
        # Initialize Telegram bot if token is available
        self.telegram_enabled = hasattr(settings, 'TELEGRAM_BOT_TOKEN') and settings.TELEGRAM_BOT_TOKEN
        if self.telegram_enabled:
            try:
                self.telegram_bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                logger.info("Telegram bot initialized successfully")
            except InvalidToken:
                logger.warning("Invalid Telegram bot token provided")
                self.telegram_enabled = False
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
                self.telegram_enabled = False
        else:
            logger.info("Telegram notifications disabled - no token configured")
        
        # Check email configuration
        self.email_enabled = all(hasattr(settings, attr) and getattr(settings, attr) 
                               for attr in ['SMTP_SERVER', 'SMTP_USERNAME', 'SMTP_PASSWORD'])
        if not self.email_enabled:
            logger.info("Email notifications disabled - missing configuration")

    async def notify_trade(self, trade_data):
        """Send trade notification via configured channels"""
        try:
            message = self._format_trade_message(trade_data)
            
            if self.telegram_enabled and self.telegram_bot:
                await self._send_telegram(message)
            
            if self.email_enabled:
                await self._send_email(message)
                
            logger.info(f"✅ Trade notification sent: {trade_data['symbol']}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")
            return False

    def _format_trade_message(self, trade_data):
        """Format trade data into a readable message"""
        return (
            f"🔔 Trade Alert\n"
            f"Symbol: {trade_data['symbol']}\n"
            f"Type: {trade_data['type']}\n"
            f"Quantity: {trade_data['quantity']}\n"
            f"Price: {trade_data['price']}"
        )

    async def _send_telegram(self, message: str):
        """Send Telegram notification"""
        try:
            for subscriber in self.subscribers:
                if subscriber.get("telegram_id"):
                    await self.telegram_bot.send_message(
                        chat_id=subscriber["telegram_id"],
                        text=message
                    )
        except Exception as e:
            logger.error(f"Telegram notification failed: {e}")

    async def _send_email(self, message: str, subject_prefix: str = "INFO"):
        """Send email notification"""
        try:
            if not self.email_server:
                self.email_server = smtplib.SMTP(settings.SMTP_SERVER)
                self.email_server.starttls()
                self.email_server.login(
                    settings.SMTP_USERNAME,
                    settings.SMTP_PASSWORD
                )
                
            msg = MIMEText(message)
            msg['Subject'] = f"[{subject_prefix}] Trading Alert"
            msg['From'] = settings.SMTP_FROM_EMAIL
            
            for subscriber in self.subscribers:
                if subscriber.get("email"):
                    msg['To'] = subscriber["email"]
                    self.email_server.send_message(msg)
                    
        except Exception as e:
            logger.error(f"Email notification failed: {e}")

    def add_subscriber(self, email: Optional[str] = None, 
                      telegram_id: Optional[str] = None):
        """Add notification subscriber"""
        self.subscribers.append({
            "email": email,
            "telegram_id": telegram_id
        })

notification_manager = NotificationManager() 
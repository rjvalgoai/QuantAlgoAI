import telegram
import asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os
from dotenv import load_dotenv
from core.logger import logger

load_dotenv()

class TradingBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.bot = None
        self.initialize_bot()

    def initialize_bot(self):
        try:
            self.bot = telegram.Bot(token=self.token)
            logger.info("Telegram bot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {e}")

    async def send_trade_alert(self, trade_data):
        if not self.bot:
            return False

        emoji = "🟢" if trade_data['order_type'] == 'BUY' else "🔴"
        message = f"""
{emoji} Trade Alert!

Symbol: {trade_data['symbol']}
Type: {trade_data['order_type']}
Quantity: {trade_data['quantity']}
Price: {trade_data['price']}

P&L: {trade_data.get('realized_pnl', 'N/A')}
Confidence: {trade_data.get('confidence_score', 'N/A')}

Stop Loss: {trade_data.get('stop_loss', 'N/A')}
Take Profit: {trade_data.get('take_profit', 'N/A')}
        """

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode='Markdown'
            )
            logger.info("Trade alert sent to Telegram")
            return True
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            return False

    async def send_system_alert(self, alert_type, message):
        if not self.bot:
            return False

        alert_message = f"""
⚠️ System Alert: {alert_type}

{message}
        """

        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=alert_message,
                parse_mode='Markdown'
            )
            logger.info(f"System alert sent to Telegram: {alert_type}")
            return True
        except Exception as e:
            logger.error(f"Failed to send system alert: {e}")
            return False

    async def start_command(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 Trading Bot Online!\n\nUse /status to check system status\n/positions to view open positions"
        )

    async def status_command(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        # Implement status check logic
        pass

    async def positions_command(self, update: telegram.Update, context: ContextTypes.DEFAULT_TYPE):
        # Implement positions check logic
        pass

    def run(self):
        """Run the bot in polling mode"""
        app = ApplicationBuilder().token(self.token).build()
        
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("positions", self.positions_command))
        
        logger.info("Starting Telegram bot polling...")
        app.run_polling()

# Singleton instance
trading_bot = TradingBot()

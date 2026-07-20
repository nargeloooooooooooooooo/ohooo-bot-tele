#!/usr/bin/env python3
"""
OHOOO BOT - Advanced Telegram Group Manager
Created by: Kknarz
GitHub: https://github.com/Kknarz/ohooo-bot
"""

import asyncio
import logging
import sys
from datetime import datetime

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import BOT_TOKEN, BOT_NAME
from utils.database import Database
from handlers.admin import AdminHandlers
from handlers.user import UserHandlers
from handlers.group import GroupHandlers
from handlers.games import GameHandlers

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler(f'logs/{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class OHOOOBot:
    def __init__(self):
        self.db = Database()
        self.admin_handlers = AdminHandlers()
        self.user_handlers = UserHandlers()
        self.group_handlers = GroupHandlers()
        self.game_handlers = GameHandlers()
    
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        try:
            if update and update.message:
                await update.message.reply_text(
                    "❌ An error occurred! The developer has been notified.\n"
                    "Please try again later."
                )
        except:
            pass
    
    async def post_init(self, application: Application):
        """Post initialization tasks"""
        logger.info("Initializing database...")
        await self.db.init_db()
        logger.info("Database initialized successfully!")
        
        # Set bot commands
        await application.bot.set_my_commands([
            ("start", "Start the bot"),
            ("help", "Show help menu"),
            ("info", "Get user info"),
            ("stats", "Group statistics"),
            ("rank", "Check your rank"),
            ("top", "Top members"),
            ("meme", "Random meme"),
            ("quote", "Random quote"),
            ("tod", "Truth or Dare"),
            ("quiz", "Math quiz"),
        ])
        
        logger.info(f"✅ {BOT_NAME} is ready!")
    
    def run(self):
        """Run the bot"""
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN not found! Please set ISI_TOKEN_TELEGRAM in .env file")
            sys.exit(1)
        
        logger.info(f"🚀 Starting {BOT_NAME}...")
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).post_init(self.post_init).build()
        
        # Add error handler
        application.add_error_handler(self.error_handler)
        
        # Register handlers
        logger.info("Registering handlers...")
        
        # Admin handlers
        for handler in self.admin_handlers.get_handlers():
            application.add_handler(handler)
        
        # User handlers
        for handler in self.user_handlers.get_handlers():
            application.add_handler(handler)
        
        # Group handlers
        for handler in self.group_handlers.get_handlers():
            application.add_handler(handler)
        
        # Game handlers
        for handler in self.game_handlers.get_handlers():
            application.add_handler(handler)
        
        # Message handler for game answers
        application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.game_handlers.check_tebak
        ))
        
        logger.info("All handlers registered!")
        logger.info(f"✅ {BOT_NAME} is running...")
        
        # Start polling
        application.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function"""
    # Create necessary directories
    import os
    os.makedirs('logs', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # ASCII Art Banner
    banner = """
    ╔══════════════════════════════════════╗
    ║          🤖 OHOOO BOT 🤖           ║
    ║   Advanced Telegram Group Manager   ║
    ║         Created by Kknarz          ║
    ║    github.com/Kknarz/ohooo-bot     ║
    ╚══════════════════════════════════════╝
    """
    print(banner)
    
    # Run bot
    bot = OHOOOBot()
    
    try:
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

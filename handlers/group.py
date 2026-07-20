from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode
from utils.database import Database
from utils.helpers import Helpers
from datetime import datetime
import aiosqlite
import re

db = Database()

class GroupHandlers:
    async def welcome_new_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Welcome new members"""
        for member in update.message.new_chat_members:
            if member.id == context.bot.id:
                # Bot was added to group
                await update.message.reply_text(
                    "🎉 Thanks for adding me! Use /help to see all commands."
                )
                continue
            
            welcome_msg = Helpers.generate_welcome_message(
                "Welcome {user} to {group}! 🎉\nEnjoy your stay!",
                member,
                update.effective_chat
            )
            
            await update.message.reply_html(welcome_msg)
    
    async def goodbye_members(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Say goodbye to leaving members"""
        member = update.message.left_chat_member
        
        await update.message.reply_text(
            f"👋 Goodbye {member.first_name}! We'll miss you!"
        )
    
    async def check_afk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if mentioned user is AFK"""
        if not update.message.reply_to_message:
            return
        
        user_id = update.message.reply_to_message.from_user.id
        
        async with aiosqlite.connect('data/database.db') as db_conn:
            async with db_conn.execute('SELECT is_afk, afk_reason FROM users WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                
                if row and row[0]:
                    await update.message.reply_text(
                        f"💤 {update.message.reply_to_message.from_user.mention_html()} is AFK!\n"
                        f"📝 Reason: {row[1]}",
                        parse_mode=ParseMode.HTML
                    )
    
    async def check_return_from_afk(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check if user returned from AFK"""
        user_id = update.effective_user.id
        
        async with aiosqlite.connect('data/database.db') as db_conn:
            async with db_conn.execute('SELECT is_afk FROM users WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                
                if row and row[0]:
                    await db_conn.execute('UPDATE users SET is_afk = 0, afk_reason = NULL WHERE user_id = ?', (user_id,))
                    await db_conn.commit()
                    
                    await update.message.reply_text(
                        f"🟢 {update.effective_user.mention_html()} is back from AFK!",
                        parse_mode=ParseMode.HTML
                    )
    
    async def track_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Track messages for XP system"""
        if not update.message or not update.message.from_user:
            return
        
        user_id = update.effective_user.id
        
        # Add XP
        await db.add_xp(user_id)
    
    async def filter_messages(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Filter messages based on banned words"""
        if not update.message or not update.message.text:
            return
        
        # Example word filter (in production, load from database)
        banned_words = ['spamword1', 'spamword2']
        
        message_text = update.message.text.lower()
        
        for word in banned_words:
            if word in message_text:
                try:
                    await update.message.delete()
                    warning = await update.message.reply_text(
                        f"⚠️ {update.effective_user.mention_html()}, that word is not allowed!",
                        parse_mode=ParseMode.HTML
                    )
                    # Delete warning after 5 seconds
                    await warning.delete()
                except:
                    pass
                break
    
    async def anti_spam(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Anti-spam protection"""
        # This is a basic implementation
        # In production, use more sophisticated spam detection
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Track message timestamps
        if 'user_messages' not in context.chat_data:
            context.chat_data['user_messages'] = {}
        
        if user_id not in context.chat_data['user_messages']:
            context.chat_data['user_messages'][user_id] = []
        
        now = datetime.now()
        messages = context.chat_data['user_messages'][user_id]
        messages.append(now)
        
        # Remove old messages
        messages = [msg for msg in messages if (now - msg).seconds < 10]
        context.chat_data['user_messages'][user_id] = messages
        
        # Check spam threshold
        if len(messages) > 5:
            try:
                # Delete spam messages
                await update.message.delete()
                
                # Warn user
                await update.message.reply_text(
                    f"⚠️ {update.effective_user.mention_html()} please stop spamming!",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
    
    def get_handlers(self):
        """Return all group handlers"""
        return [
            MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, self.welcome_new_members),
            MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, self.goodbye_members),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.track_messages),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.filter_messages),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.anti_spam),
        ]

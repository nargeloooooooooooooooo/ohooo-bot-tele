from telegram import Update
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode
from utils.database import Database
from utils.decorators import rate_limit
from utils.helpers import Helpers
from datetime import datetime

db = Database()

class UserHandlers:
    @staticmethod
    @rate_limit(1)
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command"""
        user = update.effective_user
        
        await db.add_user(user.id, user.username, user.first_name, user.last_name or "")
        
        welcome_text = f"""
✨ *Welcome to OHOOO BOT, {user.first_name}!* ✨

I'm your ultimate group management bot with awesome features!

🚀 *Main Features:*
• 🛡️ Advanced group protection
• 🎮 Fun games & quizzes
• 📊 XP & ranking system
• 🤖 AI integration
• 🌐 Translation services
• 📈 Group analytics

💡 *Quick Start:*
• Use /help to see all commands
• Add me to your group
• Make me admin for full features

🔗 *Useful Links:*
• [GitHub Repository](https://github.com/Kknarz/ohooo-bot)
• [Report Bug](https://github.com/Kknarz/ohooo-bot/issues)

Made with ❤️ by @Kknarz
"""
        
        await update.message.reply_text(
            welcome_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    @staticmethod
    @rate_limit(1)
    async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command"""
        help_text = """
📚 *OHOOO BOT - Command List*

🛡️ *Admin Commands:*
/ban - Ban a user
/unban - Unban a user
/mute - Mute a user (time in minutes)
/unmute - Unmute a user
/kick - Kick a user
/warn - Warn a user
/pin - Pin a message
/unpin - Unpin messages
/clean - Delete messages
/filter - Add word filter

👤 *User Commands:*
/start - Start the bot
/help - Show this help
/info - Get user info
/stats - Group statistics
/rank - Check your rank
/top - Top members leaderboard
/afk - Set AFK status

🎮 *Fun Commands:*
/tod - Truth or Dare
/tebak - Word guessing game
/quiz - Math quiz
/meme - Random meme
/quote - Random quote
/joke - Random joke
/fact - Random fact

🌐 *Utility Commands:*
/weather - Check weather
/translate - Translate text
/ask - Ask AI question

💡 *Tips:*
• Reply to messages for moderation
• Use /help <command> for details
• Report bugs on GitHub

Made with ❤️ by @Kknarz
"""
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True
        )
    
    @staticmethod
    @rate_limit(2)
    async def info(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get user info"""
        user = update.effective_user
        if update.message.reply_to_message:
            user = update.message.reply_to_message.from_user
        
        user_data = await db.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found in database!")
            return
        
        _, username, first_name, last_name, warns, is_banned, xp, level, msg_count, is_afk, afk_reason, joined = user_data
        
        info_text = f"""
👤 *User Information*

*Basic Info:*
• Name: {first_name} {last_name or ''}
• Username: @{username or 'N/A'}
• User ID: `{user.id}`
• Joined: {joined[:10]}

*Stats:*
• Level: {level}
• XP: {xp}/{level * 100}
• Messages: {msg_count}
• Progress: {Helpers.get_progress_bar((xp % 100), 10)}

*Status:*
• Warnings: {warns}/3
• Banned: {'❌ Yes' if is_banned else '✅ No'}
• AFK: {'💤 Yes - ' + afk_reason if is_afk else '🟢 Active'}
"""
        
        await update.message.reply_text(
            info_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    @staticmethod
    @rate_limit(2)
    async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Group statistics"""
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ This command works only in groups!")
            return
        
        chat = update.effective_chat
        stats = await db.get_group_stats(chat.id)
        
        stats_text = f"""
📊 *Group Statistics*

*{chat.title}*

• Total Members: {await chat.get_member_count()}
• Total Bans: {stats['total_bans']}
• Total Warnings: {stats['total_warns']}

*Chat Info:*
• Chat ID: `{chat.id}`
• Type: {chat.type.title()}
"""
        
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    @staticmethod
    @rate_limit(5)
    async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Top users leaderboard"""
        top_users = await db.get_top_users(10)
        
        if not top_users:
            await update.message.reply_text("❌ No data available!")
            return
        
        leaderboard = "🏆 *Top 10 Members*\n\n"
        medals = ["🥇", "🥈", "🥉"] + ["▫️"] * 7
        
        for i, user in enumerate(top_users):
            user_id, username, first_name, xp, level = user
            name = first_name or username or str(user_id)
            leaderboard += f"{medals[i]} *{name}* - Level {level} ({xp} XP)\n"
        
        await update.message.reply_text(
            leaderboard,
            parse_mode=ParseMode.MARKDOWN
        )
    
    @staticmethod
    @rate_limit(3)
    async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check user rank"""
        user = update.effective_user
        user_data = await db.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text("❌ You're not in the database yet!")
            return
        
        _, username, first_name, last_name, warns, is_banned, xp, level, msg_count = user_data[:10]
        
        rank_text = f"""
🎖 *Your Rank*

*{first_name}*
• Level: {level}
• XP: {xp}
• Progress: {Helpers.get_progress_bar((xp % 100), 10)}
• Next Level: {100 - (xp % 100)} XP needed
• Messages: {msg_count}
"""
        
        await update.message.reply_text(
            rank_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    @staticmethod
    @rate_limit(2)
    async def afk(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Set AFK status"""
        reason = ' '.join(context.args) if context.args else "No reason"
        
        async with aiosqlite.connect('data/database.db') as db_conn:
            await db_conn.execute(
                'UPDATE users SET is_afk = 1, afk_reason = ? WHERE user_id = ?',
                (reason, update.effective_user.id)
            )
            await db_conn.commit()
        
        await update.message.reply_text(
            f"💤 {update.effective_user.mention_html()} is now AFK!\n"
            f"📝 Reason: {reason}",
            parse_mode=ParseMode.HTML
        )
    
    @staticmethod
    @rate_limit(3)
    async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get weather info"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /weather <city>")
            return
        
        city = ' '.join(context.args)
        weather_info = await Helpers.get_weather(city)
        
        if weather_info:
            await update.message.reply_text(weather_info)
        else:
            await update.message.reply_text("❌ Could not fetch weather data. Check API key or city name.")
    
    @staticmethod
    @rate_limit(3)
    async def translate(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Translate text"""
        if not context.args or len(context.args) < 2:
            await update.message.reply_text("❌ Usage: /translate <target_lang> <text>")
            return
        
        target_lang = context.args[0]
        text = ' '.join(context.args[1:])
        
        translated = await Helpers.translate_text(text, target_lang)
        
        if translated:
            await update.message.reply_text(
                f"🌐 *Translation* ({target_lang}):\n\n{translated}",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await update.message.reply_text("❌ Translation failed!")
    
    def get_handlers(self):
        """Return all user handlers"""
        return [
            CommandHandler("start", self.start),
            CommandHandler("help", self.help),
            CommandHandler("info", self.info),
            CommandHandler("stats", self.stats),
            CommandHandler("top", self.top),
            CommandHandler("rank", self.rank),
            CommandHandler("afk", self.afk),
            CommandHandler("weather", self.weather),
            CommandHandler("translate", self.translate),
        ]

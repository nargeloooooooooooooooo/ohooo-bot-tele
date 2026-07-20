from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from collections import defaultdict

# Rate limiting
user_last_command = defaultdict(datetime.now)

def rate_limit(seconds=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
            user_id = update.effective_user.id
            now = datetime.now()
            
            if user_id in user_last_command:
                time_diff = (now - user_last_command[user_id]).total_seconds()
                if time_diff < seconds:
                    await update.message.reply_text(
                        f"⏳ Please wait {seconds - time_diff:.1f} seconds before using this command again."
                    )
                    return
            
            user_last_command[user_id] = now
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = await update.effective_chat.get_member(update.effective_user.id)
        
        if user.status not in ['creator', 'administrator']:
            await update.message.reply_text("❌ This command is for admins only!")
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

def group_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        if update.effective_chat.type == 'private':
            await update.message.reply_text("❌ This command can only be used in groups!")
            return
        
        return await func(update, context, *args, **kwargs)
    return wrapper

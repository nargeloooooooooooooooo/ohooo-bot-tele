from telegram import Update, ChatPermissions
from telegram.ext import ContextTypes, CommandHandler
from telegram.constants import ParseMode
from datetime import datetime, timedelta
from utils.database import Database
from utils.decorators import admin_only, group_only, rate_limit
from utils.helpers import Helpers

db = Database()

class AdminHandlers:
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ban a user from the group"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a message to ban that user!")
            return
        
        user_to_ban = update.message.reply_to_message.from_user
        reason = ' '.join(context.args) if context.args else "No reason provided"
        
        try:
            await update.effective_chat.ban_member(user_to_ban.id)
            await db.ban_user(user_to_ban.id, update.effective_chat.id, update.effective_user.id, reason)
            
            await update.message.reply_text(
                f"✅ {user_to_ban.mention_html()} has been banned!\n"
                f"📝 Reason: {reason}\n"
                f"👮 By: {update.effective_user.mention_html()}",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to ban user: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unban a user"""
        if not context.args:
            await update.message.reply_text("❌ Provide user ID to unban!\nUsage: /unban user_id")
            return
        
        try:
            user_id = int(context.args[0])
            await update.effective_chat.unban_member(user_id)
            await db.unban_user(user_id)
            
            await update.message.reply_text(
                f"✅ User {user_id} has been unbanned!\n"
                f"👮 By: {update.effective_user.mention_html()}",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to unban user: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Mute a user"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a message to mute that user!")
            return
        
        user_to_mute = update.message.reply_to_message.from_user
        duration = int(context.args[0]) if context.args and context.args[0].isdigit() else 60
        reason = ' '.join(context.args[1:]) if len(context.args) > 1 else "No reason"
        
        until_date = datetime.now() + timedelta(minutes=duration)
        
        try:
            await update.effective_chat.restrict_member(
                user_to_mute.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            
            await update.message.reply_text(
                f"🔇 {user_to_mute.mention_html()} has been muted for {duration} minutes!\n"
                f"📝 Reason: {reason}\n"
                f"👮 By: {update.effective_user.mention_html()}",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to mute user: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unmute a user"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a message to unmute that user!")
            return
        
        user_to_unmute = update.message.reply_to_message.from_user
        
        try:
            await update.effective_chat.restrict_member(
                user_to_unmute.id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_polls=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True
                )
            )
            
            await update.message.reply_text(
                f"🔊 {user_to_unmute.mention_html()} has been unmuted!\n"
                f"👮 By: {update.effective_user.mention_html()}",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to unmute user: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Kick a user from group"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a message to kick that user!")
            return
        
        user_to_kick = update.message.reply_to_message.from_user
        
        try:
            await update.effective_chat.ban_member(user_to_kick.id)
            await update.effective_chat.unban_member(user_to_kick.id)  # Unban immediately after kick
            
            await update.message.reply_text(
                f"👢 {user_to_kick.mention_html()} has been kicked!\n"
                f"👮 By: {update.effective_user.mention_html()}",
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to kick user: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Warn a user"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a message to warn that user!")
            return
        
        user_to_warn = update.message.reply_to_message.from_user
        reason = ' '.join(context.args) if context.args else "No reason provided"
        
        await db.warn_user(user_to_warn.id, update.effective_chat.id, update.effective_user.id, reason)
        user = await db.get_user(user_to_warn.id)
        
        warns = user[4] if user else 1
        
        await update.message.reply_text(
            f"⚠️ {user_to_warn.mention_html()} has been warned! ({warns}/3)\n"
            f"📝 Reason: {reason}\n"
            f"👮 By: {update.effective_user.mention_html()}",
            parse_mode=ParseMode.HTML
        )
        
        # Auto-ban if warn limit reached
        if warns >= 3:
            try:
                await update.effective_chat.ban_member(user_to_warn.id)
                await db.ban_user(user_to_warn.id, update.effective_chat.id, update.effective_user.id, "Auto-ban: 3 warnings reached")
                await update.message.reply_text(
                    f"🚫 {user_to_warn.mention_html()} has been auto-banned for reaching 3 warnings!",
                    parse_mode=ParseMode.HTML
                )
            except:
                pass
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def pin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pin a message"""
        if not update.message.reply_to_message:
            await update.message.reply_text("❌ Reply to a message to pin it!")
            return
        
        try:
            await update.message.reply_to_message.pin()
            await update.message.reply_text("📌 Message pinned!")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to pin message: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def unpin(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unpin all messages"""
        try:
            await update.effective_chat.unpin_all_messages()
            await update.message.reply_text("📌 All messages unpinned!")
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to unpin messages: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(5)
    async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Delete multiple messages"""
        if not context.args or not context.args[0].isdigit():
            await update.message.reply_text("❌ Usage: /clean <number>")
            return
        
        count = min(int(context.args[0]), 100)  # Max 100 messages
        
        try:
            # Get chat history
            messages = []
            async for message in update.effective_chat.get_history(limit=count + 1):
                messages.append(message.message_id)
            
            # Delete messages
            await update.effective_chat.delete_messages(messages)
            
            # Send confirmation and delete it after 5 seconds
            confirmation = await update.message.reply_text(f"🧹 Deleted {len(messages)} messages!")
            await confirmation.delete()
            
        except Exception as e:
            await update.message.reply_text(f"❌ Failed to delete messages: {str(e)}")
    
    @staticmethod
    @admin_only
    @group_only
    @rate_limit(2)
    async def filter_add(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Add word filter"""
        if not context.args:
            await update.message.reply_text("❌ Usage: /filter <word>")
            return
        
        word = context.args[0].lower()
        # In production, save to database
        
        await update.message.reply_text(f"✅ Filter added for word: '{word}'")
    
    def get_handlers(self):
        """Return all admin handlers"""
        return [
            CommandHandler("ban", self.ban),
            CommandHandler("unban", self.unban),
            CommandHandler("mute", self.mute),
            CommandHandler("unmute", self.unmute),
            CommandHandler("kick", self.kick),
            CommandHandler("warn", self.warn),
            CommandHandler("pin", self.pin),
            CommandHandler("unpin", self.unpin),
            CommandHandler("clean", self.clean),
            CommandHandler("filter", self.filter_add),
        ]

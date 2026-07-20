from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler
from telegram.constants import ParseMode
from utils.decorators import rate_limit
from utils.helpers import Helpers
import random
import asyncio

class GameHandlers:
    def __init__(self):
        self.active_games = {}
    
    @rate_limit(3)
    async def truth_or_dare(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Truth or Dare game"""
        truths = [
            "What's the most embarrassing thing you've ever done?",
            "What's your biggest fear?",
            "What's the last lie you told?",
            "What's your most controversial opinion?",
            "What's the weirdest dream you've ever had?",
            "What's something you've never told anyone?",
            "What's your guilty pleasure?",
            "What's the worst date you've ever been on?"
        ]
        
        dares = [
            "Send the last photo in your gallery",
            "Use only emojis for the next 5 minutes",
            "Post 'I love OHOOO Bot' as your status",
            "Send a voice message singing a song",
            "Share your most used emoji",
            "Tell a joke (must be original)",
            "Describe yourself in 3 words",
            "Share your phone's wallpaper"
        ]
        
        keyboard = [
            [InlineKeyboardButton("🟢 Truth", callback_data="tod_truth"),
             InlineKeyboardButton("🔴 Dare", callback_data="tod_dare")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🎮 *Truth or Dare*\n\nChoose your fate! 👇",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def tod_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle Truth or Dare callback"""
        query = update.callback_query
        await query.answer()
        
        choice = query.data.split('_')[1]
        
        if choice == "truth":
            question = random.choice(self.truths) if hasattr(self, 'truths') else "What's your secret talent?"
            await query.edit_message_text(
                f"🟢 *Truth:*\n\n{question}\n\nAnswer honestly! 😄",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            dare = random.choice(self.dares) if hasattr(self, 'dares') else "Do 10 pushups!"
            await query.edit_message_text(
                f"🔴 *Dare:*\n\n{dare}\n\nGood luck! 💪",
                parse_mode=ParseMode.MARKDOWN
            )
    
    @rate_limit(3)
    async def tebak_kata(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Word guessing game"""
        words = {
            'python': 'A popular programming language named after a snake',
            'telegram': 'A messaging app with bots and channels',
            'computer': 'An electronic device for processing data',
            'internet': 'A global network connecting millions of devices',
            'robot': 'A machine capable of carrying out actions automatically',
            'galaxy': 'A system of millions or billions of stars',
            'elephant': 'The largest land animal on Earth',
            'chocolate': 'A sweet food made from cocoa beans'
        }
        
        word = random.choice(list(words.keys()))
        hint = words[word]
        
        self.active_games[update.effective_chat.id] = {
            'word': word,
            'hint': hint,
            'attempts': 0
        }
        
        # Show hint with hidden letters
        hidden = ' '.join(['_' for _ in word])
        
        await update.message.reply_text(
            f"🎮 *Word Guessing Game*\n\n"
            f"📝 Hint: {hint}\n"
            f"🔤 Word: `{hidden}`\n"
            f"📏 Length: {len(word)} letters\n\n"
            f"Type your guess in chat! Use /tebak to see hint again.",
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def check_tebak(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check word guessing answers"""
        chat_id = update.effective_chat.id
        
        if chat_id not in self.active_games:
            return
        
        game = self.active_games[chat_id]
        user_guess = update.message.text.lower()
        
        if user_guess == game['word']:
            attempts = game['attempts']
            await update.message.reply_text(
                f"🎉 Congratulations {update.effective_user.mention_html()}!\n"
                f"You guessed the word '*{game['word']}*' in {attempts} attempts!",
                parse_mode=ParseMode.HTML
            )
            del self.active_games[chat_id]
        else:
            game['attempts'] += 1
            if game['attempts'] >= 5:
                await update.message.reply_text(
                    f"❌ Game Over! The word was '*{game['word']}*'",
                    parse_mode=ParseMode.MARKDOWN
                )
                del self.active_games[chat_id]
    
    @rate_limit(3)
    async def math_quiz(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Math quiz game"""
        operations = ['+', '-', '*']
        op = random.choice(operations)
        
        if op == '+':
            a, b = random.randint(1, 100), random.randint(1, 100)
            answer = a + b
        elif op == '-':
            a, b = random.randint(50, 100), random.randint(1, 49)
            answer = a - b
        else:
            a, b = random.randint(1, 12), random.randint(1, 12)
            answer = a * b
        
        question = f"{a} {op} {b}"
        
        self.active_games[f"math_{update.effective_chat.id}"] = {
            'answer': answer,
            'question': question
        }
        
        # Options
        options = [answer]
        while len(options) < 4:
            fake = answer + random.randint(-10, 10)
            if fake != answer and fake not in options:
                options.append(fake)
        random.shuffle(options)
        
        keyboard = [
            [InlineKeyboardButton(str(opt), callback_data=f"math_{opt}")]
            for opt in options
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🧮 *Math Quiz*\n\n"
            f"Question: `{question} = ?`\n\n"
            f"Choose your answer:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def math_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle math quiz answers"""
        query = update.callback_query
        await query.answer()
        
        answer = int(query.data.split('_')[1])
        chat_id = query.message.chat_id
        game_key = f"math_{chat_id}"
        
        if game_key in self.active_games:
            correct = self.active_games[game_key]['answer']
            
            if answer == correct:
                await query.edit_message_text(
                    f"🎉 Correct! The answer is *{correct}*!\n\n"
                    f"Great job {query.from_user.mention_html()}!",
                    parse_mode=ParseMode.HTML
                )
            else:
                await query.edit_message_text(
                    f"❌ Wrong! The correct answer was *{correct}*\n\n"
                    f"Better luck next time!",
                    parse_mode=ParseMode.MARKDOWN
                )
            
            del self.active_games[game_key]
    
    @rate_limit(3)
    async def meme(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send random meme"""
        url, title = await Helpers.get_random_meme()
        
        if url:
            await update.message.reply_photo(
                photo=url,
                caption=f"📸 {title}\n\nPowered by @ohooo_bot"
            )
        else:
            await update.message.reply_text("❌ Failed to fetch meme. Try again later!")
    
    @rate_limit(3)
    async def quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send random quote"""
        quote_text = await Helpers.get_random_quote()
        
        await update.message.reply_text(
            f"💭 *Quote of the Day*\n\n{quote_text}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    @rate_limit(3)
    async def joke(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send random joke"""
        joke_text = await Helpers.get_random_joke()
        
        await update.message.reply_text(
            f"😄 *Joke Time!*\n\n{joke_text}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    @rate_limit(3)
    async def fact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send random fact"""
        fact_text = await Helpers.get_random_fact()
        
        await update.message.reply_text(
            f"🤓 *Random Fact*\n\n{fact_text}",
            parse_mode=ParseMode.MARKDOWN
        )
    
    def get_handlers(self):
        """Return all game handlers"""
        return [
            CommandHandler("tod", self.truth_or_dare),
            CommandHandler("tebak", self.tebak_kata),
            CommandHandler("quiz", self.math_quiz),
            CommandHandler("meme", self.meme),
            CommandHandler("quote", self.quote),
            CommandHandler("joke", self.joke),
            CommandHandler("fact", self.fact),
            CallbackQueryHandler(self.tod_callback, pattern="^tod_"),
            CallbackQueryHandler(self.math_callback, pattern="^math_"),
        ]

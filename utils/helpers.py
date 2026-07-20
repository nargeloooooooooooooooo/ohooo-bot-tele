import random
import emoji
from datetime import datetime
import requests
from config import *

class Helpers:
    @staticmethod
    def generate_welcome_message(template, user, group):
        """Generate personalized welcome message"""
        return template.format(
            user=user.mention_html(),
            group=group.title,
            time=datetime.now().strftime("%H:%M")
        )
    
    @staticmethod
    def get_random_emoji():
        """Get random emoji"""
        emojis = list(emoji.EMOJI_DATA.keys())
        return random.choice(emojis)
    
    @staticmethod
    def format_duration(seconds):
        """Format seconds to readable duration"""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if secs > 0:
            parts.append(f"{secs}s")
        
        return " ".join(parts) if parts else "0s"
    
    @staticmethod
    async def get_random_meme():
        """Fetch random meme from API"""
        try:
            response = requests.get('https://meme-api.com/gimme')
            if response.status_code == 200:
                data = response.json()
                return data['url'], data['title']
        except:
            pass
        return None, None
    
    @staticmethod
    async def get_random_quote():
        """Fetch random quote"""
        try:
            response = requests.get('https://api.quotable.io/random')
            if response.status_code == 200:
                data = response.json()
                return f"\"{data['content']}\" - {data['author']}"
        except:
            pass
        return "Life is what happens when you're busy making other plans. - John Lennon"
    
    @staticmethod
    async def get_random_fact():
        """Fetch random fact"""
        try:
            response = requests.get('https://uselessfacts.jsph.pl/random.json?language=en')
            if response.status_code == 200:
                data = response.json()
                return data['text']
        except:
            pass
        return "Honey never spoils. Archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old!"
    
    @staticmethod
    async def get_random_joke():
        """Fetch random joke"""
        try:
            response = requests.get('https://v2.jokeapi.dev/joke/Any?type=single')
            if response.status_code == 200:
                data = response.json()
                return data['joke']
        except:
            pass
        return "Why don't scientists trust atoms? Because they make up everything!"
    
    @staticmethod
    async def get_weather(city):
        """Get weather information"""
        if not WEATHER_API_KEY:
            return None
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                temp = data['main']['temp']
                feels_like = data['main']['feels_like']
                humidity = data['main']['humidity']
                description = data['weather'][0]['description']
                
                return f"""
🌍 Weather in {city.title()}:
🌡 Temperature: {temp}°C
🤔 Feels like: {feels_like}°C
💧 Humidity: {humidity}%
📝 {description.title()}
"""
        except:
            pass
        return None
    
    @staticmethod
    async def translate_text(text, target_lang='en'):
        """Translate text using Google Translate"""
        try:
            from deep_translator import GoogleTranslator
            translated = GoogleTranslator(source='auto', target=target_lang).translate(text)
            return translated
        except:
            return None
    
    @staticmethod
    def get_progress_bar(percentage, length=10):
        """Create progress bar"""
        filled = int(length * percentage / 100)
        bar = '█' * filled + '░' * (length - filled)
        return f"[{bar}] {percentage}%"

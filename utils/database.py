import aiosqlite
from datetime import datetime
from config import DATABASE_PATH

class Database:
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    async def init_db(self):
        async with aiosqlite.connect(self.db_path) as db:
            # Users table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    warns INTEGER DEFAULT 0,
                    is_banned INTEGER DEFAULT 0,
                    xp INTEGER DEFAULT 0,
                    level INTEGER DEFAULT 1,
                    messages_count INTEGER DEFAULT 0,
                    is_afk INTEGER DEFAULT 0,
                    afk_reason TEXT,
                    joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Groups table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS groups (
                    group_id INTEGER PRIMARY KEY,
                    group_name TEXT,
                    welcome_message TEXT DEFAULT 'Welcome {user} to {group}! 🎉',
                    rules TEXT,
                    is_protected INTEGER DEFAULT 0,
                    mute_duration INTEGER DEFAULT 3600,
                    warn_limit INTEGER DEFAULT 3,
                    filters TEXT,
                    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Warnings table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS warnings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    group_id INTEGER,
                    admin_id INTEGER,
                    reason TEXT,
                    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (group_id) REFERENCES groups (group_id)
                )
            ''')
            
            # Bans table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS bans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    group_id INTEGER,
                    admin_id INTEGER,
                    reason TEXT,
                    ban_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    unban_date TIMESTAMP,
                    is_permanent INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (group_id) REFERENCES groups (group_id)
                )
            ''')
            
            # Mutes table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS mutes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    group_id INTEGER,
                    admin_id INTEGER,
                    reason TEXT,
                    mute_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    unmute_date TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (group_id) REFERENCES groups (group_id)
                )
            ''')
            
            await db.commit()
    
    async def add_user(self, user_id, username, first_name, last_name=""):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                VALUES (?, ?, ?, ?)
            ''', (user_id, username, first_name, last_name))
            await db.commit()
    
    async def get_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('SELECT * FROM users WHERE user_id = ?', (user_id,)) as cursor:
                return await cursor.fetchone()
    
    async def add_xp(self, user_id, amount=10):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users 
                SET xp = xp + ?, messages_count = messages_count + 1
                WHERE user_id = ?
            ''', (amount, user_id))
            
            # Check level up
            async with db.execute('SELECT xp, level FROM users WHERE user_id = ?', (user_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    xp, level = row
                    new_level = (xp // 100) + 1
                    if new_level > level:
                        await db.execute('UPDATE users SET level = ? WHERE user_id = ?', (new_level, user_id))
            
            await db.commit()
    
    async def warn_user(self, user_id, group_id, admin_id, reason=""):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                UPDATE users SET warns = warns + 1 WHERE user_id = ?
            ''', (user_id,))
            
            await db.execute('''
                INSERT INTO warnings (user_id, group_id, admin_id, reason)
                VALUES (?, ?, ?, ?)
            ''', (user_id, group_id, admin_id, reason))
            
            await db.commit()
    
    async def ban_user(self, user_id, group_id, admin_id, reason="", duration=None):
        async with aiosqlite.connect(self.db_path) as db:
            is_permanent = 0 if duration else 1
            
            await db.execute('''
                UPDATE users SET is_banned = 1 WHERE user_id = ?
            ''', (user_id,))
            
            unban_date = None
            if duration:
                from datetime import timedelta
                unban_date = datetime.now() + timedelta(seconds=duration)
            
            await db.execute('''
                INSERT INTO bans (user_id, group_id, admin_id, reason, unban_date, is_permanent)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, group_id, admin_id, reason, unban_date, is_permanent))
            
            await db.commit()
    
    async def unban_user(self, user_id):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('UPDATE users SET is_banned = 0 WHERE user_id = ?', (user_id,))
            await db.execute('UPDATE bans SET unban_date = CURRENT_TIMESTAMP WHERE user_id = ? AND is_permanent = 0', (user_id,))
            await db.commit()
    
    async def get_group_stats(self, group_id):
        async with aiosqlite.connect(self.db_path) as db:
            stats = {}
            
            async with db.execute('SELECT COUNT(*) FROM users') as cursor:
                row = await cursor.fetchone()
                stats['total_users'] = row[0] if row else 0
            
            async with db.execute('SELECT COUNT(*) FROM bans WHERE group_id = ?', (group_id,)) as cursor:
                row = await cursor.fetchone()
                stats['total_bans'] = row[0] if row else 0
            
            async with db.execute('SELECT COUNT(*) FROM warnings WHERE group_id = ?', (group_id,)) as cursor:
                row = await cursor.fetchone()
                stats['total_warns'] = row[0] if row else 0
            
            return stats
    
    async def get_top_users(self, limit=10):
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT user_id, username, first_name, xp, level 
                FROM users 
                ORDER BY xp DESC 
                LIMIT ?
            ''', (limit,)) as cursor:
                return await cursor.fetchall()

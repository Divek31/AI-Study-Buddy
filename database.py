import sqlite3
import bcrypt
import os
import json
from datetime import datetime, date, timedelta

DB_NAME = "study_buddy.db"

def get_db_connection():
    """Returns a connection to the SQLite database."""
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    """Initializes the database tables if they do not exist."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            current_streak INTEGER DEFAULT 0,
            last_study_date TEXT,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            badges TEXT DEFAULT '[]'
        )
    ''')
    
    # Safe Migrations for existing DBs
    try:
        c.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")
        c.execute("ALTER TABLE users ADD COLUMN level INTEGER DEFAULT 1")
        c.execute("ALTER TABLE users ADD COLUMN badges TEXT DEFAULT '[]'")
    except sqlite3.OperationalError:
        pass # Columns already exist
    
    # Subjects table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            color TEXT DEFAULT '#6366f1',
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Materials table
    c.execute('''
        CREATE TABLE IF NOT EXISTS materials (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            uploaded_at TEXT NOT NULL,
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    # Quizzes table
    c.execute('''
        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER,
            topic TEXT NOT NULL,
            data_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    # Flashcards table
    c.execute('''
        CREATE TABLE IF NOT EXISTS flashcards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject_id INTEGER,
            topic TEXT NOT NULL,
            data_json TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        )
    ''')
    
    # Study Logs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL, 
            duration_minutes INTEGER NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Search History table
    c.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            query TEXT NOT NULL,
            overview_text TEXT NOT NULL,
            youtube_links TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Study Plans table
    c.execute('''
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            hours INTEGER NOT NULL,
            plan_markdown TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# --- Auth Functions ---
def create_user(username, password):
    """Creates a new user account. Returns True if successful, False if username exists."""
    conn = get_db_connection()
    c = conn.cursor()
    
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False  # Username already exists
    finally:
        conn.close()
        
    return success

def verify_user(username, password):
    """Verifies user credentials. Returns the user dict if successful, None otherwise."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT id, username, password_hash, current_streak, last_study_date, xp, level, badges FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    
    if row is None:
        return None
        
    stored_hash = row[2]
    if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
        return {
            "id": row[0],
            "username": row[1],
            "current_streak": row[3],
            "last_study_date": row[4],
            "xp": row[5] if row[5] is not None else 0,
            "level": row[6] if row[6] is not None else 1,
            "badges": json.loads(row[7]) if row[7] else []
        }
    return None

def update_study_streak(user_id):
    """Updates the user's study streak based on current date."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT current_streak, last_study_date FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return 0
        
    current_streak = row[0]
    last_study_date_str = row[1]
    today_str = date.today().isoformat()
    
    if not last_study_date_str:
        # First time studying
        new_streak = 1
    elif last_study_date_str == today_str:
        # Already studied today, streak stays the same
        new_streak = current_streak
    else:
        last_date = date.fromisoformat(last_study_date_str)
        delta = date.today() - last_date
        
        if delta.days == 1:
            # Studied yesterday, continue streak
            new_streak = current_streak + 1
        else:
            # Missed a day, reset streak
            new_streak = 1
            
    c.execute("UPDATE users SET current_streak = ?, last_study_date = ? WHERE id = ?", (new_streak, today_str, user_id))
    conn.commit()
    conn.close()
    
    return new_streak

# --- Subject Functions ---
def add_subject(user_id, name, color="#6366f1"):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("INSERT INTO subjects (user_id, name, color) VALUES (?, ?, ?)", (user_id, name, color))
    conn.commit()
    subject_id = c.lastrowid
    conn.close()
    return subject_id

def get_subjects(user_id):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id, name, color FROM subjects WHERE user_id = ?", (user_id,))
    subjects = [{"id": row[0], "name": row[1], "color": row[2]} for row in c.fetchall()]
    conn.close()
    return subjects

# --- Material Functions ---
def add_material(subject_id, name, file_path, file_type):
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.now().isoformat()
    c.execute("INSERT INTO materials (subject_id, name, file_path, file_type, uploaded_at) VALUES (?, ?, ?, ?, ?)", 
              (subject_id, name, file_path, file_type, now_str))
    conn.commit()
    conn.close()

def get_materials(subject_id=None, user_id=None):
    """Fetch materials for a specific subject, or all materials for a user."""
    conn = get_db_connection()
    c = conn.cursor()
    
    if subject_id:
        c.execute("SELECT id, name, file_path, file_type, uploaded_at FROM materials WHERE subject_id = ?", (subject_id,))
    elif user_id:
        c.execute('''
            SELECT m.id, m.name, m.file_path, m.file_type, m.uploaded_at, s.name 
            FROM materials m 
            JOIN subjects s ON m.subject_id = s.id 
            WHERE s.user_id = ?
        ''', (user_id,))
    else:
        return []
        
    rows = c.fetchall()
    conn.close()
    
    materials = []
    for row in rows:
        mat_dict = {
            "id": row[0],
            "name": row[1],
            "file_path": row[2],
            "file_type": row[3],
            "uploaded_at": row[4]
        }
        if user_id and not subject_id:
            mat_dict["subject_name"] = row[5]
        materials.append(mat_dict)
        
    return materials

# --- Assessment Functions ---
def add_quiz(user_id, subject_id, topic, data):
    """Saves a generated quiz to the database."""
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.now().isoformat()
    data_json = json.dumps(data) if not isinstance(data, str) else data
    
    c.execute("INSERT INTO quizzes (user_id, subject_id, topic, data_json, created_at) VALUES (?, ?, ?, ?, ?)",
              (user_id, subject_id, topic, data_json, now_str))
    conn.commit()
    quiz_id = c.lastrowid
    conn.close()
    return quiz_id

def get_quizzes(user_id):
    """Fetches all generated quizzes for a user."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT q.id, q.subject_id, q.topic, q.data_json, q.created_at, s.name 
        FROM quizzes q 
        LEFT JOIN subjects s ON q.subject_id = s.id 
        WHERE q.user_id = ?
        ORDER BY q.created_at DESC
    ''', (user_id,))
    
    rows = c.fetchall()
    conn.close()
    
    quizzes = []
    for row in rows:
        quizzes.append({
            "id": row[0],
            "subject_id": row[1],
            "topic": row[2],
            "data_json": json.loads(row[3]) if isinstance(row[3], str) else row[3],
            "created_at": row[4],
            "subject_name": row[5] if row[5] else "Global"
        })
    return quizzes

def add_flashcard(user_id, subject_id, topic, data):
    """Saves a generated flashcard set to the database."""
    conn = get_db_connection()
    c = conn.cursor()
    now_str = datetime.now().isoformat()
    # Flashcards typically come in as markdown string, but just in case it's dict-based, stringify it
    data_json = json.dumps(data) if not isinstance(data, str) else data
    
    c.execute("INSERT INTO flashcards (user_id, subject_id, topic, data_json, created_at) VALUES (?, ?, ?, ?, ?)",
              (user_id, subject_id, topic, data_json, now_str))
    conn.commit()
    flashcard_id = c.lastrowid
    conn.close()
    return flashcard_id

def get_flashcards(user_id):
    """Fetches all generated flashcards for a user."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('''
        SELECT f.id, f.subject_id, f.topic, f.data_json, f.created_at, s.name 
        FROM flashcards f 
        LEFT JOIN subjects s ON f.subject_id = s.id 
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (user_id,))
    
    rows = c.fetchall()
    conn.close()
    
    flashcards = []
    for row in rows:
        flashcards.append({
            "id": row[0],
            "subject_id": row[1],
            "topic": row[2],
            "data": row[3], # Stored as string markdown typically
            "created_at": row[4],
            "subject_name": row[5] if row[5] else "Global"
        })
    return flashcards

# --- Gamification Functions ---
def add_xp(user_id, xp_gain):
    """Adds XP to user and handles leveling up. Returns state dict."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT xp, level FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return None
        
    current_xp = row[0] if row[0] is not None else 0
    current_level = row[1] if row[1] is not None else 1
    
    new_xp = current_xp + xp_gain
    new_level = (new_xp // 100) + 1  # 100 XP per level
    
    leveled_up = new_level > current_level
    
    c.execute("UPDATE users SET xp = ?, level = ? WHERE id = ?", (new_xp, new_level, user_id))
    conn.commit()
    conn.close()
    
    return {
        "xp": new_xp,
        "level": new_level,
        "leveled_up": leveled_up
    }

def award_badge(user_id, badge_name):
    """Awards a badge if the user doesn't already have it."""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute("SELECT badges FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    if not row:
        conn.close()
        return False
        
    badges = json.loads(row[0]) if row[0] else []
    
    if badge_name not in badges:
        badges.append(badge_name)
        c.execute("UPDATE users SET badges = ? WHERE id = ?", (json.dumps(badges), user_id))
        conn.commit()
        conn.close()
        return True # Newly awarded
        
    conn.close()
    return False # Already had it

def log_study_session(user_id, activity_type, duration_minutes):
    """Logs a study session for analytics."""
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT INTO study_logs (user_id, activity_type, duration_minutes, created_at) VALUES (?, ?, ?, ?)",
              (user_id, activity_type, duration_minutes, now))
    conn.commit()
    conn.close()

def get_study_analytics(user_id, days=7):
    """Returns aggregated study minutes per day for the last N days."""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Calculate cutoff date
    cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
    
    # Fetch logs
    c.execute("""
        SELECT DATE(created_at) as log_date, SUM(duration_minutes) as total_minutes
        FROM study_logs
        WHERE user_id = ? AND created_at >= ?
        GROUP BY log_date
        ORDER BY log_date ASC
    """, (user_id, cutoff_date))
    
    rows = c.fetchall()
    conn.close()
    
    
    return [{"date": row[0], "minutes": row[1]} for row in rows]

def add_search_history(user_id, query, overview_text, youtube_links):
    """Saves a quick start search to history."""
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT INTO search_history (user_id, query, overview_text, youtube_links, created_at) VALUES (?, ?, ?, ?, ?)",
              (user_id, query, overview_text, youtube_links, now))
    conn.commit()
    conn.close()

def get_search_history(user_id):
    """Retrieves all Quick Start searches for a user."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, query, overview_text, youtube_links, created_at FROM search_history WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def add_study_plan(user_id, hours, plan_markdown):
    """Saves an AI-generated study plan."""
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("INSERT INTO study_plans (user_id, hours, plan_markdown, created_at) VALUES (?, ?, ?, ?)",
              (user_id, hours, plan_markdown, now))
    conn.commit()
    conn.close()

def get_study_plans(user_id):
    """Retrieves all generated study plans for a user."""
    conn = get_db_connection()
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT id, hours, plan_markdown, created_at FROM study_plans WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]

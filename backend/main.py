from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List
import sqlite3
import uuid

app = FastAPI(title="Telegram Chat API")

# ========== НАСТРОЙКА CORS ==========
# Разрешаем запросы с фронтенда на Netlify и локальной разработки
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # для локальной разработки
        "https://telegram-chat-task-frontend.netlify.app"  # ваш фронтенд на Netlify
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =====================================

# Модель для сообщения
class Message(BaseModel):
    id: str = ""
    text: str
    timestamp: str = ""
    isMine: bool = True

# ========== РАБОТА С БАЗОЙ ДАННЫХ ==========
def get_db_connection():
    """Создаёт и возвращает соединение с SQLite базой данных."""
    conn = sqlite3.connect('chat.db')
    # Чтобы результаты запросов возвращались как словари
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Создаёт таблицу для сообщений, если её ещё нет."""
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            text TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            isMine BOOLEAN NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Инициализируем базу при старте приложения
init_database()
# ===========================================

@app.get("/")
def read_root():
    return {"message": "Telegram Chat API is running"}

@app.get("/messages", response_model=List[Message])
def get_messages():
    conn = get_db_connection()
    # Получаем все сообщения, отсортированные по времени (старые сверху)
    cursor = conn.execute('SELECT * FROM messages ORDER BY timestamp')
    messages = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return messages

@app.post("/messages", response_model=Message)
def create_message(message: Message):
    # Генерируем ID и время, если они не пришли с фронтенда
    if not message.id:
        message.id = str(uuid.uuid4())
    if not message.timestamp:
        message.timestamp = datetime.now().isoformat()

    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO messages (id, text, timestamp, isMine) VALUES (?, ?, ?, ?)',
            (message.id, message.text, message.timestamp, message.isMine)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Message with this ID already exists")
    finally:
        conn.close()

    return message
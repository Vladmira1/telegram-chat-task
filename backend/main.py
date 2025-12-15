from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List
import uuid
import random
import asyncio

# Ответы
auto_responses = [
    "Привет! Как дела?",
    "Интересно...",
    "Согласен с тобой",
    "Расскажи подробнее",
    "У меня тоже так бывает",
    "Хорошая мысль!",
    "Продолжай..."
]

app = FastAPI(title="Telegram Chat API")

# Разрешаем запросы с фронтенда
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Адрес React приложения
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Модель для сообщения
class Message(BaseModel):
    id: str = ""
    text: str
    timestamp: str = ""
    isMine: bool = True


# Хранилище в памяти
messages_db = []


@app.get("/")
def read_root():
    return {"message": "Telegram Chat API is running"}


@app.get("/messages", response_model=List[Message])
def get_messages():
    return messages_db


@app.post("/messages", response_model=Message)
async def create_message(message: Message):
    if not message.id:
        message.id = str(uuid.uuid4())
    if not message.timestamp:
        message.timestamp = datetime.now().isoformat()

    messages_db.append(message)

    # Имитация ответа через 1-3 секунды
    if message.isMine:
        await asyncio.sleep(random.uniform(1.0, 3.0))
        response_message = Message(
            id=str(uuid.uuid4()),
            text=random.choice(auto_responses),
            timestamp=datetime.now().isoformat(),
            isMine=False
        )
        messages_db.append(response_message)

    return message
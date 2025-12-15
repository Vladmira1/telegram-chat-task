import React, { useState, useEffect, useRef } from 'react';
import './App.css';

interface Message {
  id: string;
  text: string;
  timestamp: string;
  isMine: boolean;
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // Загрузка сообщений при запуске
  useEffect(() => {
    fetch('https://telegram-chat-backend-9lwd.onrender.com/messages')
      .then(res => res.json())
      .then(data => setMessages(data))
      .catch(error => console.error('Error loading messages:', error));
  }, []);

  // Прокрутка вниз при новых сообщениях
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = async () => {
    const text = newMessage.trim();
    if (!text || isSending) return;
    
    setIsSending(true);
    const messageToSend: Message = {
      text: text,
      isMine: true,
      id: '',
      timestamp: ''
    };

    try {
      const response = await fetch('https://telegram-chat-backend-9lwd.onrender.com/messages', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(messageToSend)
      });
      
      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();
      // ДОБАВЛЯЕМ СООБЩЕНИЕ СРАЗУ
      setMessages(prev => [...prev, data]);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
      alert('Ошибка при отправке сообщения');
    } finally {
      setIsSending(false);
    }
  };

  // Форматирование времени
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  return (
    <div className="App">
      {/* Шапка как в Telegram */}
      <div className="header">
        <div className="avatar">В</div>
        <div className="contact-info">
          <h2>Telegram Chat</h2>
          <p>онлайн</p>
        </div>
      </div>

      {/* Контейнер сообщений */}
      <div className="chat-container" ref={chatContainerRef}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', color: '#7f91a4', marginTop: '50px' }}>
            <p>Нет сообщений</p>
            <p>Начните общение!</p>
          </div>
        ) : (
          messages.map(msg => (
            <div 
              key={msg.id} 
              className={`message ${msg.isMine ? 'my-message' : 'other-message'}`}
            >
              <p>{msg.text}</p>
              <div className="message-time">{formatTime(msg.timestamp)}</div>
            </div>
          ))
        )}
      </div>

      {/* Поле ввода */}
      <div className="input-area">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Введите сообщение..."
          onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
          disabled={isSending}
        />
        <button 
          className="send-button"
          onClick={sendMessage} 
          disabled={!newMessage.trim() || isSending}
          title="Отправить"
        />
      </div>
    </div>
  );
}

export default App;
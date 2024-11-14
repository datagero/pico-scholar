import React, { useState } from 'react';
import Draggable from 'react-draggable';
import styles from './Funnel.module.css';

const AIAssistantChat = ({ onClose }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
      setTimeout(() => {
        setMessages((prevMessages) => [...prevMessages, { text: "I'm here to help with your PDF content.", sender: 'assistant' }]);
      }, 500);
    }
  };

  return (
    <Draggable>
      <div className={styles.chatWindow}>
        <div className={styles.chatHeader}>
          <h3>AI PDF Assistant</h3>
          <button onClick={onClose} className={styles.closeButton}>×</button>
        </div>
        <div className={styles.chatBody}>
          {messages.map((message, index) => (
            <div key={index} className={message.sender === 'user' ? styles.userMessage : styles.assistantMessage}>
              {message.text}
            </div>
          ))}
        </div>
        <form onSubmit={handleSubmit} className={styles.chatInputContainer}>
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className={styles.chatInput}
          />
          <button type="submit" className={styles.sendButton}>Send</button>
        </form>
      </div>
    </Draggable>
  );
};

export default AIAssistantChat;

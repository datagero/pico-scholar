import React, { useState, useRef, useEffect } from 'react';
import Draggable from 'react-draggable';
import styles from './Funnel.module.css';

const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

const AIAssistantChat = ({ onClose, documentID }) => {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [isFirstMessagesSent, setIsFirstMessagesSent] = useState(false);
  const chatBodyRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (input.trim()) {
      setMessages([...messages, { text: input, sender: 'user' }]);
      setInput('');
      
      try {
        const response = await sendChat(input, documentID);
        setMessages((prevMessages) => [...prevMessages, { text: response.response, sender: 'assistant' }]);
      } catch (error) {
        setMessages((prevMessages) => [...prevMessages, { text: 'Error fetching response. Please try again.', sender: 'assistant' }]);
      }
    }
  };

  useEffect(() => {
    if (!isFirstMessagesSent) {
      // Optionally send the initial message to the backend
      (async () => {
        try {
          const response = await sendChat("Introduce the article I am chatting with", documentID);
          setMessages((prevMessages) => [...prevMessages, { text: response.response, sender: 'assistant' }]);
          setMessages((prevMessages) => [...prevMessages, { text: 'Ask me more about this study!', sender: 'assistant' }]);
        } catch (error) {
          console.error('Error fetching initial response:', error);
        }
        setIsFirstMessagesSent(true);
      })();
    }
  }, [isFirstMessagesSent, documentID]);

  useEffect(() => {
    if (chatBodyRef.current) {
      chatBodyRef.current.scrollTop = chatBodyRef.current.scrollHeight;
    }
  }, [messages]);

  const sendChat = async (query, documentID) => {
    try {
      const url = `${BASE_URL}/rag/projects/1/docu_chat/query_bot?query=${query}&document_id=${documentID}`;
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
        },
      });
      const responseData = await response.json();
      if (!response.ok) {
        throw new Error(`Server error: ${JSON.stringify(responseData)}`);
      }
      return responseData;
    } catch (error) {
      console.error('Chat request failed:', error);
      throw error;
    }
  };

  return (
    <Draggable>
      <div className={styles.chatWindow}>
        <div className={styles.chatHeader}>
          <h3>PDF AI Assistant</h3>
          <button onClick={onClose} className={styles.closeButton}>×</button>
        </div>
        <div 
          ref={chatBodyRef}
          className={styles.chatBody}
          style={{ scrollBehavior: 'smooth' }}
        >
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

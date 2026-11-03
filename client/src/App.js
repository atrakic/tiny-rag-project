import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

let baseHostUrl = process.env.REACT_APP_API_URL;

// eslint-disable-next-line no-restricted-globals
if (location.host === 'localhost:3000') {
  baseHostUrl = 'http://127.0.0.1:8000/api';
}

const initialMessages = [
  {
    id: 1,
    role: 'assistant',
    text: 'Ask me anything about your data.',
  },
];

function App() {
  const [messages, setMessages] = useState(initialMessages);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    const query = input.trim();
    if (!query || isLoading) {
      return;
    }

    const userMessage = { id: Date.now(), role: 'user', text: query };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${baseHostUrl}/chat`, { query });
      const answer = response.data.answer || 'I could not find relevant information in your documents.';
      const sources = response.data.sources || [];
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: 'assistant',
          text: answer,
          sources,
        },
      ]);
    } catch (error) {
      console.error('Error fetching chat response:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 2,
          role: 'assistant',
          text: 'I could not access the document assistant right now. Please try again.',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-shell">
      <div className="chat-panel">
        <header className="chat-header">
          <h1>Tiny Local RAG</h1>
          <p>Ask questions about your data.</p>
        </header>

        <div className="message-list">
          {messages.map((message) => (
            <div key={message.id} className={`message-row ${message.role}`}>
              <div className="message-bubble">
                <div className="message-role">{message.role === 'user' ? 'You' : 'Assistant'}</div>
                <div className="message-text">{message.text}</div>
                {message.sources && message.sources.length > 0 && (
                  <ul className="source-list">
                    {message.sources.map((source, index) => (
                      <li key={`${source.source}-${index}`}>
                        <strong>{source.source}</strong>
                        <span> · score {Number(source.score).toFixed(3)}</span>
                        <div>{source.text}</div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message-row assistant">
              <div className="message-bubble loading">Thinking…</div>
            </div>
          )}
        </div>

        <form className="chat-form" onSubmit={handleSubmit}>
          <input
            type="text"
            value={input}
            onChange={(event) => setInput(event.target.value)}
            placeholder="Ask about your documents... ex: summarize contents"
            aria-label="Ask about your documents"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Thinking...' : 'Ask'}
          </button>
        </form>
      </div>
    </div>
  );
}

export default App;

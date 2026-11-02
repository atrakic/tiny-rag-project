import React, { useState } from 'react';
import InputForm from './InputForm';
import DocumentsDisplay from './DocumentsDisplay';
import axios from 'axios';
import './App.css';

let baseHostUrl = process.env.REACT_APP_API_URL;

// eslint-disable-next-line no-restricted-globals
if (location.host === 'localhost:3000') {
  baseHostUrl = 'http://127.0.0.1:8000/api';
}

function App() {
  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSearchSubmit = async (query) => {
    setIsLoading(true);
    setError('');

    try {
      const result = await axios.post(`${baseHostUrl}/search`, { query });
      setDocuments(result.data.results || []);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError('Failed to fetch search results.');
      setDocuments([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app container mt-5">
      <h1 className="text-center mb-4">RAG Search</h1>
      <div className="search-section card mb-4">
        <div className="card-body">
          <h2 className="card-title">Ask a question about your data</h2>
          <p className="card-text">Search your indexed documents with semantic retrieval.</p>
          <InputForm onSubmit={handleSearchSubmit} placeholder="Ask about your data" />

          {isLoading ? (
            <div className="text-center">
              <div className="spinner-border text-primary" role="status">
                <span className="visually-hidden">Loading...</span>
              </div>
            </div>
          ) : (
            <>
              {error && <p className="text-danger">{error}</p>}
              <DocumentsDisplay documents={documents} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
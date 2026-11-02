import React from 'react';

function DocumentsDisplay({ documents }) {
  // Only render the section if documents array is not empty
  return documents.length > 0 && (
    <div>
      <h4 className="subheader">Relevant matches:</h4>
      <ul>
        {documents.map((doc, index) => (
          <li key={index}>{doc.text} - Score: {doc.score}</li>
        ))}
      </ul>
    </div>
  );
}

export default DocumentsDisplay;

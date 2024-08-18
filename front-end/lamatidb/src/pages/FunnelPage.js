// FunnelPage.js

// Contains the main page components, which typically represent different routes in your application.
// The page where the search results are displayed in the funnel view.

import React from 'react';
import { useLocation } from 'react-router-dom';

const FunnelPage = () => {
  const location = useLocation();
  const { results } = location.state || {};

  return (
    <div>
      <h1>Welcome to Results Analyser!</h1>
      {results && results.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th style={{ width: '800px' }}>Summary</th> {/* Set a specific width */}
              <th style={{ width: '500px' }}>Abstract</th> {/* Set a specific width */}
              <th style={{ width: '500px' }}>PICO</th> {/* Set a specific width */}
              <th>Funnel Stage</th>
              <th>Reviewed</th>
            </tr>
          </thead>
          <tbody>
            {results.map((result, index) => (
              <tr key={index}>
                {/* Merged and Compact Summary Column with Narrow Width */}
                <td style={{ 
                  whiteSpace: 'normal', 
                  width: '200px', 
                  overflow: 'hidden', 
                  textOverflow: 'ellipsis',
                  wordWrap: 'break-word'
                }}>
                  <strong>{result.title}</strong><br />
                  {result.year}, {result.authors}<br />
                  ID: {result.source_id}, Similarity: {result.similarity}
                </td>

                <td>{result.abstract}</td>

                {/* Merged PICO Column */}
                <td>
                  <strong>P:</strong> {result.pico_p} <br />
                  <strong>I:</strong> {result.pico_i} <br />
                  <strong>C:</strong> {result.pico_c} <br />
                  <strong>O:</strong> {result.pico_o}
                </td>

                <td>{result.funnel_stage}</td>
                <td>{result.is_reviewed ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <p>No results found.</p>
      )}
    </div>
  );
};


export default FunnelPage;

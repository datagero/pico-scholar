import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faThumbtack, faUpload, faArrowRight, faTimes } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { searchQuery } from '../services/searchService';

const HomePage = () => {
  const [query, setQuery] = useState('');
  const [isAdvancedSearch, setIsAdvancedSearch] = useState(false);
  const [pinnedSearches, setPinnedSearches] = useState([
    { id: 1, text: 'Past Search 1: "Machine Learning in Medical Imaging"' },
    { id: 2, text: 'Past Search 2: "AI Predictive Models for Disease"' },
    { id: 3, text: 'Past Search 3: "Natural Language Processing in Healthcare"' },
  ]);

  const navigate = useNavigate();

  const handleInputChange = (e) => {
    setQuery(e.target.value);
  };

  const clearInput = () => {
    setQuery('');
  };

  const handleAdvancedSearchChange = () => {
    setIsAdvancedSearch(!isAdvancedSearch);
  };

  const deletePinnedSearch = (id) => {
    setPinnedSearches(pinnedSearches.filter(search => search.id !== id));
  };

  const handleSearch = async () => {
    if (query.trim()) {
      try {
        const data = await searchQuery(query);
        console.log('Search results:', data); // Handle the response data as needed
        navigate('/results', { state: { results: data.results } }); // Pass results to FunnelPage
      } catch (error) {
        console.error('Error during the search request:', error);
      }
    } else {
      alert('Please enter a search query');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="homepage">
      <h2>Your Gateway to Groundbreaking Research</h2>
      
      <div className="search-bar-container">
        <button className="upload-button">
          <FontAwesomeIcon icon={faUpload} />
        </button>
        <input 
          type="text" 
          placeholder="Ask a research query"  
          className="search-bar" 
          value={query}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}  // Add this line
        />
        {query && (
          <button className="clear-button" onClick={clearInput}>
            <FontAwesomeIcon icon={faTimes} />
          </button>
        )}
        <button className="search-button" onClick={handleSearch}>
          <FontAwesomeIcon icon={faArrowRight} />
        </button>
      </div>

      <div className="advanced-search-container">
        <label>
          <input 
            type="checkbox" 
            checked={isAdvancedSearch} 
            onChange={handleAdvancedSearchChange} 
          />
          Advanced Search
        </label>
      </div>

      {isAdvancedSearch && (
        <div className="advanced-search-popup">
          <h4>Filter by:</h4>
          <label>
            <input type="checkbox" /> Date
            <input type="text" className="advanced-input" placeholder="Enter date..." />
          </label>
          <label>
            <input type="checkbox" /> Location
            <input type="text" className="advanced-input" placeholder="Enter location..." />
          </label>
          <label>
            <input type="checkbox" /> Demographic
            <input type="text" className="advanced-input" placeholder="Enter demographic..." />
          </label>
          <label>
            <input type="checkbox" /> Design/methodology
            <input type="text" className="advanced-input" placeholder="Enter design/methodology..." />
          </label>
          <label>
            <input type="checkbox" /> Search strategy (add more keywords)
            <input type="text" className="advanced-input" placeholder="Enter search strategy..." />
          </label>
          <label>
            <input type="checkbox" /> Type of intervention
            <input type="text" className="advanced-input" placeholder="Enter intervention type..." />
          </label>
          <label>
            <input type="checkbox" /> PICO
            <input type="text" className="advanced-input" placeholder="Enter PICO criteria..." />
          </label>
        </div>
      )}

      <div className="pinned-searches">
        <h3 className="pinned-title">Research Project: AI in Healthcare</h3>
        <ul>
          {pinnedSearches.map(search => (
            <li key={search.id}>
              <FontAwesomeIcon icon={faThumbtack} className="pin-icon" />
              <a href="#search1" className="past-search-link">{search.text}</a>
              <button className="delete-button" onClick={() => deletePinnedSearch(search.id)}>
                <FontAwesomeIcon icon={faTimes} />
              </button>
            </li>
          ))}
        </ul>
      </div>

      <div className="guideline-section">
        <h3 className="guideline-title">Research Query Guideline</h3>
        <div className="guideline-box">
          <p>
            Welcome to our research platform, designed to streamline your search for academic papers and research articles. This tool allows you to quickly find relevant studies and literature in your field of interest, leveraging advanced search options to narrow down results based on specific criteria.
          </p>
          <p>
            You can perform a basic search using the query input above, or opt for the advanced search mode to filter by date, location, demographic details, and more. Our platform also supports search strategies based on PICO (Population, Intervention, Comparison, Outcome) to enhance the precision of your research.
          </p>
          <p>
            The pinned searches section above lets you save and manage your previous searches, so you can easily revisit important studies. Click on the "X" button to remove any searches that are no longer needed. We hope this tool aids you in your research journey by making information more accessible and manageable.
          </p>
        </div>
      </div>
    </div>
  );
};

export default HomePage;

import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faThumbtack, faUpload, faArrowRight, faTimes, faSpinner, faArrowRight as faArrowRightIcon } from '@fortawesome/free-solid-svg-icons';
import { useNavigate } from 'react-router-dom';
import { searchQuery, translateTerms } from '../services/searchService';
import Tooltip from '@mui/material/Tooltip';

const HomePage = () => {
  const [query, setQuery] = useState('');
  const [isAdvancedSearch, setIsAdvancedSearch] = useState(false);
  const [scientificNotations, setScientificNotations] = useState({});
  const [isScientificQueryVisible, setIsScientificQueryVisible] = useState(false);

  // State to capture human-readable user inputs
  const [yearFrom, setYearFrom] = useState('');
  const [yearTo, setYearTo] = useState('');
  const [country, setCountry] = useState('');
  const [randomizedTrial, setRandomizedTrial] = useState('');
  const [population, setPopulation] = useState('');
  const [intervention, setIntervention] = useState('');
  const [comparison, setComparison] = useState('');
  const [outcome, setOutcome] = useState('');

  const handleTranslateTerms = async () => {
    const terms = {
      "Year of Publication": `From ${yearFrom} to ${yearTo}`,
      "Country of Publication": country,
      "Does the Study use Randomized Trial?": randomizedTrial,
      "P (Population)": population,
      "I (Intervention)": intervention,
      "C (Comparison)": comparison,
      "O (Outcome)": outcome
    };

    try {
      const translatedTerms = await translateTerms(terms);
      console.log('Translated Terms:', translatedTerms); // Add this line to debug
      setScientificNotations(translatedTerms.scientific_notation);
    } catch (error) {
      console.error('Translation failed:', error);
      // Handle error (e.g., show notification)
    }
  };

  React.useEffect(() => {
    console.log('Updated scientificNotations:', scientificNotations);
  }, [scientificNotations]);

  const [pinnedSearches, setPinnedSearches] = useState([
    { id: 1, text: 'Project Query 1: "Effectiveness of Statins in Preventing Cardiovascular Events"' },
    { id: 2, text: 'Project Query 2: "Comparative Effectiveness of Different Classes of Antihypertensive Drugs"' },
    { id: 3, text: 'Project Query 3: "Impact of Lifestyle Changes on Cardiovascular Health"' },
  ]);
  const [loading, setLoading] = useState(false);

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
      setLoading(true);
      try {
        const data = await searchQuery(query);
        console.log('Search results:', data);
        navigate('/results', { state: { results: data.results } });
      } catch (error) {
        console.error('Error during the search request:', error);
      } finally {
        setLoading(false);
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

  const handleScientificQueryClick = () => {
    setIsScientificQueryVisible(true);
    handleTranslateTerms();
  };

  return (
    <div className="homepage">
      <h2>The Gateway to Research Relevant to You</h2>

      <div className="search-container">
        <div className="search-bar-container">
          <button className="upload-button">
            <FontAwesomeIcon icon={faUpload} />
          </button>
          <input 
            type="text" 
            placeholder="Search for Evidence on Your Research Question"  
            className="search-bar" 
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
          />
          {query && (
            <button className="clear-button" onClick={clearInput}>
              <FontAwesomeIcon icon={faTimes} />
            </button>
          )}
          <button className="search-button" onClick={handleSearch}>
            <FontAwesomeIcon icon={faArrowRight} />
          </button>
          {loading && (
            <div className="spinner">
              <FontAwesomeIcon icon={faSpinner} spin />
            </div>
          )}
        </div>
      </div>

      <div className="advanced-search-toggle">
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
        <div className={`advanced-search-wrapper ${isScientificQueryVisible ? 'two-boxes' : 'one-box'}`}>
          <div className="advanced-search-box">
            <div className="advanced-search-content">
              <div className="advanced-search-fields">
                <label className="field-label">
                  <Tooltip title="Specify the year range of publication">
                    <span className="field-name">Year of Publication</span>
                  </Tooltip>
                  <div className="field-inputs">
                    <input
                      type="text"
                      className="advanced-input"
                      placeholder="From..."
                      value={yearFrom}
                      onChange={(e) => setYearFrom(e.target.value)}
                    />
                    <input
                      type="text"
                      className="advanced-input"
                      placeholder="To..."
                      value={yearTo}
                      onChange={(e) => setYearTo(e.target.value)}
                    />
                  </div>
                </label>
                
                <label className="field-label">
                  <Tooltip title="Start typing the country name to filter the list">
                    <span className="field-name">Country of Publication</span>
                  </Tooltip>
                  <input
                    type="text"
                    className="advanced-input"
                    placeholder="Enter country..."
                    list="countries"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                  />
                  <datalist id="countries">
                    <option value="United States" />
                    <option value="United Kingdom" />
                    <option value="Canada" />
                    <option value="Australia" />
                  </datalist>
                </label>
                
                <label className="field-label">
                  <Tooltip title="Indicate whether the study uses a randomized trial methodology">
                    <span className="field-name">Does the Study use Randomized Trial?</span>
                  </Tooltip>
                  <div className="field-inputs">
                    <label>
                      <input
                        type="radio"
                        name="randomizedTrial"
                        value="Yes"
                        checked={randomizedTrial === 'Yes'}
                        onChange={(e) => setRandomizedTrial(e.target.value)}
                      /> Yes
                    </label>
                    <label>
                      <input
                        type="radio"
                        name="randomizedTrial"
                        value="No"
                        checked={randomizedTrial === 'No'}
                        onChange={(e) => setRandomizedTrial(e.target.value)}
                      /> No
                    </label>
                  </div>
                </label>
                
                <label className="field-label">
                  <Tooltip title="Search strategy based on PICO criteria">
                    <span className="field-name">PICO</span>
                  </Tooltip>
                  <div className="pico-container">
                    <div className="pico-item">
                      <span className="field-name">P (Population)</span>
                      <input
                        type="text"
                        className="advanced-input"
                        placeholder="Enter population criteria..."
                        value={population}
                        onChange={(e) => setPopulation(e.target.value)}
                      />
                    </div>
                    <div className="pico-item">
                      <span className="field-name">I (Intervention)</span>
                      <input
                        type="text"
                        className="advanced-input"
                        placeholder="Enter intervention criteria..."
                        value={intervention}
                        onChange={(e) => setIntervention(e.target.value)}
                      />
                    </div>
                    <div className="pico-item">
                      <span className="field-name">C (Comparison)</span>
                      <input
                        type="text"
                        className="advanced-input"
                        placeholder="Enter comparison criteria..."
                        value={comparison}
                        onChange={(e) => setComparison(e.target.value)}
                      />
                    </div>
                    <div className="pico-item">
                      <span className="field-name">O (Outcome)</span>
                      <input
                        type="text"
                        className="advanced-input"
                        placeholder="Enter outcome criteria..."
                        value={outcome}
                        onChange={(e) => setOutcome(e.target.value)}
                      />
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>

          {!isScientificQueryVisible && (
            <div className="convert-button-container">
              <button className="convert-button" onClick={handleScientificQueryClick}>
                Scientific Query
                <FontAwesomeIcon icon={faArrowRightIcon} />
              </button>
            </div>
          )}

      {isScientificQueryVisible && (
        <div className="advanced-search-box">
          <div className="advanced-search-content">
            <div className="advanced-search-fields">
              <label className="field-label">
                <Tooltip title="Scientific year range for publication">
                  <span className="field-name">Scientific Notation Translation</span>
                </Tooltip>
                <div className="field-inputs">
                  <input
                    type="text"
                    className="advanced-input"
                    placeholder="Scientific From..."
                    value={scientificNotations['Year of Publication'] ? scientificNotations['Year of Publication'].split(' ')[0] : ''}
                  />
                  <input
                    type="text"
                    className="advanced-input"
                    placeholder="Scientific To..."
                    value={scientificNotations['Year of Publication'] ? scientificNotations['Year of Publication'].split(' ')[1] : ''}
                  />
                </div>
              </label>
              
              <label className="field-label">
                <Tooltip title="Scientific filter by country">
                  <span className="field-name">~</span>
                </Tooltip>
                <input
                  type="text"
                  className="advanced-input"
                  placeholder="Scientific country..."
                  value={scientificNotations['Country of Publication'] || ''}
                />
              </label>
              
              <label className="field-label">
                <Tooltip title="Indicate scientific use of randomized trial methodology">
                  <span className="field-name">~</span>
                </Tooltip>
                <div className="field-inputs">
                  <label>
                    <input
                      type="radio"
                      name="randomizedTrial"
                      value="Yes"
                      checked={scientificNotations['Does the Study use Randomized Trial?'] === 'Yes'}
                    /> Yes
                  </label>
                  <label>
                    <input
                      type="radio"
                      name="randomizedTrial"
                      value="No"
                      checked={scientificNotations['Does the Study use Randomized Trial?'] === 'No'}
                    /> No
                  </label>
                </div>
              </label>
              
              <label className="field-label">
                <Tooltip title="Scientific strategy based on PICO criteria">
                  <span className="field-name">~</span>
                </Tooltip>
                <div className="pico-container">
                  <div className="pico-item">
                    <span className="field-name">~</span>
                    <input
                      type="text"
                      className="advanced-input"
                      placeholder="Scientific population..."
                      value={scientificNotations['P (Population)'] || ''}
                    />
                  </div>
                  <div className="pico-item">
                    <span className="field-name">~</span>
                    <input
                      type="text"
                      className="advanced-input"
                      placeholder="Scientific intervention..."
                      value={scientificNotations['I (Intervention)'] || ''}
                    />
                  </div>
                  <div className="pico-item">
                    <span className="field-name">~</span>
                    <input
                      type="text"
                      className="advanced-input"
                      placeholder="Scientific comparison..."
                      value={scientificNotations['C (Comparison)'] || ''}
                    />
                  </div>
                  <div className="pico-item">
                    <span className="field-name">~</span>
                    <input
                      type="text"
                      className="advanced-input"
                      placeholder="Scientific outcome..."
                      value={scientificNotations['O (Outcome)'] || ''}
                    />
                  </div>
                    </div>
                  </label>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="pinned-searches">
        <h3 className="pinned-title">Project Question: <br></br> What are the most effective strategies for improving patient outcomes in cardiovascular diseases?</h3>
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
  )
}

export default HomePage;

import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import FunnelTable from '../components/Funnel/FunnelTable';
import styles from '../components/Funnel/Funnel.module.css';
import { filterByStatus } from '../services/statusService';

const FunnelPage = () => {
  const location = useLocation();
  const initialResults = location.state?.results || []; // Get initial results from the main page search
  const [papers, setPapers] = useState(initialResults);
  const [currentStatus, setCurrentStatus] = useState('Identified');
  const [selectedPapers, setSelectedPapers] = useState([]);
  const [semanticSearchQuery, setSemanticSearchQuery] = useState('');
  const [narrowSearch, setNarrowSearch] = useState(false);
  const [narrowField, setNarrowField] = useState('All Fields');

  const handleSelectPaper = (paperId) => {
    setSelectedPapers((prevSelected) => {
      if (prevSelected.includes(paperId)) {
        return prevSelected.filter(id => id !== paperId);
      } else {
        return [...prevSelected, paperId];
      }
    });
  };

  const handleStageChange = (event) => {
    const newStage = event.target.value;
    const updatedPapers = papers; // To implement in backend newStage and selectedPapers (global)
    setPapers(updatedPapers);
    setSelectedPapers([]); // Clear selection after status change
  };

  const handleStatusButtonClick = (status) => {
    setCurrentStatus(status);
  };

  const handleSearch = () => {
    // Logic for handling the search within the current status
    console.log("Searching for:", semanticSearchQuery);
  };

  const clearSearch = () => {
    setSemanticSearchQuery('');
  };

  const filteredPapers = filterByStatus(currentStatus);
  // papers.filter(paper => paper.funnel_stage === currentStatus); // to be managed by backend API call.

  return (
    <div className={styles.container}>
      <div className={styles.statusButtonsContainer}>
        <button 
          className={`${styles.statusButton} ${currentStatus === 'Identified' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Identified')}
        >
          Identified
        </button>
        <button 
          className={`${styles.statusButton} ${currentStatus === 'Screened' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Screened')}
        >
          Screened
        </button>
        <button 
          className={`${styles.statusButton} ${currentStatus === 'Sought for Retrieval' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Sought for Retrieval')}
        >
          Sought for Retrieval
        </button>
        <button 
          className={`${styles.statusButton} ${currentStatus === 'Assessed for Eligibility' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Assessed for Eligibility')}
        >
          Assessed for Eligibility
        </button>
        <button 
          className={`${styles.statusButton} ${currentStatus === 'Systematic Literature Review' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Systematic Literature Review')}
        >
          Systematic Literature Review
        </button>
      </div>
      
      <div className={styles.controlsContainer}>
        {/* Selected and Change Status on one line */}
        <div className={styles.selectedStatusContainer}>
          <span className={styles.selectedText}>Selected: {selectedPapers.length}</span>
          <div className={styles.statusChange}>
            <span>Change Status: </span>
            <select 
              value={currentStatus} 
              onChange={handleStageChange} 
              className={styles.dropdown}
            >
              <option value="Identified">Identified</option>
              <option value="Screened">Screened</option>
              <option value="Sought for Retrieval">Sought for Retrieval</option>
              <option value="Assessed for Eligibility">Assessed for Eligibility</option>
              <option value="Systematic Literature Review">Systematic Literature Review</option>
            </select>
          </div>
        </div>

        {/* Search and Narrow Search under Selected and Change Status */}
        <div className={styles.searchAndNarrowContainer}>
          <div className={styles.searchContainer}>
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Search in current list of papers."
              value={searchQuery}
              onChange={(e) => setSemanticSearchQuery(e.target.value)}
            />
            <button className={styles.clearButton} onClick={clearSearch}>
              &times;
            </button>
            <button className={styles.searchButton} onClick={handleSearch}>
              ➔
            </button>
          </div>

          <div className={styles.narrowSearchContainer}>
            <label>
              <input 
                type="checkbox" 
                checked={narrowSearch} 
                onChange={() => setNarrowSearch(!narrowSearch)} 
              />
              Narrow search to fields
            </label>
            {narrowSearch && (
              <select 
                value={narrowField} 
                onChange={(e) => setNarrowField(e.target.value)} 
                className={styles.dropdown}
              >
                <option value="All Fields">All Fields</option>
                <option value="Abstract">Abstract</option>
                <option value="Patient">Patient</option>
                <option value="Intervention">Intervention</option>
                <option value="Comparison">Comparison</option>
                <option value="Outcome">Outcome</option>
              </select>
            )}
          </div>
        </div>
      </div>

      <FunnelTable
        results={filteredPapers}
        selectedPapers={selectedPapers}
        handleSelectPaper={handleSelectPaper}
        funnelStage={currentStatus}
      />
    </div>
  );
};

export default FunnelPage;

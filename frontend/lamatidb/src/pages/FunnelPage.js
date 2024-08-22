import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import FunnelTable from '../components/Funnel/FunnelTable';
import styles from '../components/Funnel/Funnel.module.css';
import { filterByStatus, updateDocumentStatuses } from '../services/statusService';
import { semanticSearchQuery } from '../services/searchService';

const FunnelPage = () => {
  const location = useLocation();
  const initialResults = location.state?.results || []; // Get initial results from the main page search
  const [papers, setPapers] = useState(initialResults);
  const [sourceIds, setSourceIds] = useState(initialResults.map(paper => paper.source_id));
  const [displayIds, setDisplayPaperIds] = useState(initialResults.map(paper => paper.source_id));
  const [displayPapers, setDisplayPapers] = useState(initialResults);
  const [currentStatus, setCurrentStatus] = useState('Identified');
  const [selectedPapers, setSelectedPapers] = useState([]);
  const [semanticQuery, setSemanticSearchQuery] = useState('');
  // const [narrowSearch, setNarrowSearch] = useState(false);
  const [narrowFields, setNarrowFields] = useState('All Fields');

  // Run handleFilters whenever currentStatus changes
  useEffect(() => {
    handleFilters();
  }, [currentStatus]);
  const handleUpdateStatuses = async (newStage) => {
    try {
      await updateDocumentStatuses(selectedPapers, newStage);
      // Refresh the data or update the UI to reflect the status change
      handleFilters();
    } catch (error) {
      console.error('Failed to update statuses:', error);
    }
  };

  // useEffect to update displayPapers whenever displayIds or papers change
  useEffect(() => {
    const filteredPapers = displayIds
      .map(id => papers.find(paper => paper.source_id === id))
      .filter(paper => paper !== undefined);
    setDisplayPapers(filteredPapers);
  }, [displayIds, papers]);


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
    // Optional: Call an API to update the stage in the backend
    // Example: updateStage(newStage, selectedPapers);
    handleUpdateStatuses(newStage); // Update the current status with the new stage
    setSelectedPapers([]); // Clear selection after status change
  };

  const handleStatusButtonClick = (status) => {
    setCurrentStatus(status);
  };

  const handleSemanticSearch = async () => {
    if (semanticQuery.trim()) {
      try {
        const semantic_search_results = await semanticSearchQuery(semanticQuery, [narrowFields], sourceIds);
        const ids = semantic_search_results.source_ids;
        console.log('Semantic Search results:', ids);
        setDisplayPaperIds(ids);
        // TODO -> Update the UI to reflect the search results. These should be a filtered subset of the papers state.
        // Ideally, we want these sorted on the same order as the ids returned by the search.
        // The UI should have a way to "Go back to all papers" or "Clear search results"
      } catch (error) {
        console.error('Error during the search request:', error);
      }
    } else {
      alert('Please enter a search query');
    }
  };

  
  const clearSearch = () => {
    setSemanticSearchQuery('');
  };

  const handleFilters = async () => {
    try {
      console.log("Filtering papers for status:", currentStatus);
      const filteredPapers = await filterByStatus(currentStatus);
      const newPapers = filteredPapers.records;
      const newSourceIds = newPapers.map(paper => paper.source_id);

      // Update the state with the new filtered data
      setPapers(newPapers);
      setSourceIds(newSourceIds);

      // Set displayIds and displayPapers based on the newly filtered papers
      setDisplayPaperIds(newSourceIds);
      // setDisplayPapers(newPapers);

      // TODO -> We probably need to reset the counts for the funnel filters here (filteredPapers.funnel_count contains the counts after filters)
      console.log(filteredPapers); // Log filtered results for debugging
    } catch (error) {
      console.error('Error in handleFilters:', error);
    }
  };

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
          className={`${styles.statusButton} ${currentStatus === 'Sought Retrieval' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Sought Retrieval')}
        >
          Sought Retrieval
        </button>
        <button 
          className={`${styles.statusButton} ${currentStatus === 'Assessed Eligibility' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Assessed Eligibility')}
        >
          Assessed Eligibility
        </button>
        <button 
          className={`${styles.statusButton} ${currentStatus === 'Included in Review' ? styles.activeStatus : ''}`}
          onClick={() => handleStatusButtonClick('Included in Review')}
        >
          Included in Review
        </button>
      </div>
      
      <div className={styles.controlsContainer}>
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
            <option value="Sought Retrieval">Sought Retrieval</option>
            <option value="Assessed Eligibility">Assessed Eligibility</option>
            <option value="Included in Review">Included in Review</option>
          </select>
        </div>

        {/* Search and Narrow Search under Selected and Change Status */}
        <div className={styles.searchAndNarrowContainer}>
          <div className={styles.searchContainer}>
            <input
              type="text"
              className={styles.searchInput}
              placeholder="Search in current list of papers."
              value={semanticQuery}
              onChange={(e) => setSemanticSearchQuery(e.target.value)}
            />
            <button className={styles.clearButton} onClick={clearSearch}>
              &times;
            </button>
            <button className={styles.searchButton} onClick={handleSemanticSearch}>
              ➔
            </button>
          </div>

          <div className={styles.narrowSearchContainer}>
            {/* <label>
              <input 
                type="checkbox" 
                checked={narrowSearch} 
                onChange={() => {
                  setNarrowSearch(!narrowSearch);
                }} 
              />
              Narrow search to fields
            </label> */}
            {/* {narrowSearch && ( */}
            Narrow search to fields
              <select 
                value={narrowFields} 
                onChange={(e) => setNarrowFields(e.target.value)} 
                className={styles.dropdown}
              >
                <option value="All Fields">All Fields</option>
                <option value="Full Document">Full Document</option>
                <option value="Patient">Patient</option>
                <option value="Intervention">Intervention</option>
                <option value="Comparison">Comparison</option>
                <option value="Outcome">Outcome</option>
              </select>
            {/* )} */}
          </div>
        </div>
      </div>

      <FunnelTable
        results={displayPapers} // Use the papers state which contains filtered results
        selectedPapers={selectedPapers}
        handleSelectPaper={handleSelectPaper}
        funnelStage={currentStatus}
      />
    </div>
  );
};

export default FunnelPage;
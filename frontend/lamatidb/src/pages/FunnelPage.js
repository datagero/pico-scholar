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
  const [selectAll, setSelectAll] = useState(false); // State for Select All checkbox
  const [narrowFields, setNarrowFields] = useState('All Fields');
  const [showArchived, setShowArchived] = useState(false);
  const [showOnlyItemsWithPDFs, setShowOnlyItemsWithPDFs] = useState(false); // New state for "Show Only Items with PDFs"
  const [currentPage, setCurrentPage] = useState(1); // Track the current page

  // Function to update the current page
  const updateCurrentPage = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // Run handleFilters whenever currentStatus (to bulk update selected items)
  // or archivedStatus (individually select items) for a record changes
  useEffect(() => {
    handleFilters();
  }, [currentStatus, showArchived]);

  const handleUpdateStatuses = async (newStage) => {
    try {
      await updateDocumentStatuses(selectedPapers, newStage);
      handleFilters();
    } catch (error) {
      console.error('Failed to update statuses:', error);
    }
  };

  const handleArchiveRecord = () => {
    handleFilters(); // Refresh the filters
  };

  const handleToggleShowOnlyItemsWithPDFs = () => {
    setShowOnlyItemsWithPDFs((prevState) => !prevState);
  };

  // useEffect to update displayPapers whenever displayIds or papers change
  useEffect(() => {
    const filteredPapers = displayIds
      .map(id => papers.find(paper => paper.source_id === id))
      .filter(paper => paper !== undefined);
    setDisplayPapers(filteredPapers);
  }, [displayIds, papers]);

  const handleSelectPaper = (paperIds) => {
    if (Array.isArray(paperIds)) {
      setSelectedPapers(paperIds);
    } else {
      setSelectedPapers((prevSelected) => {
        if (prevSelected.includes(paperIds)) {
          return prevSelected.filter(id => id !== paperIds);
        } else {
          return [...prevSelected, paperIds];
        }
      });
    }
  };

  const handleSelectAllChange = () => {
    const allSelected = !selectAll;
    setSelectAll(allSelected);
    if (allSelected) {
      const allPaperIds = displayPapers.map(paper => paper.source_id);
      handleSelectPaper(allPaperIds);
    } else {
      handleSelectPaper([]);
    }
  };

  const handleStageChange = (event) => {
    const newStage = event.target.value;
    handleUpdateStatuses(newStage);
    setSelectedPapers([]);
  };

  const handleStatusButtonClick = (status) => {
    setCurrentStatus(status);
  };

  const handleSemanticSearch = async () => {
    if (semanticQuery.trim()) {
      try {
        const semantic_search_results = await semanticSearchQuery(semanticQuery, [narrowFields], sourceIds);
        const ids = semantic_search_results.source_ids;
        setDisplayPaperIds(ids);
      } catch (error) {
        console.error('Error during the search request:', error);
      }
    } else {
      alert('Please enter a search query');
    }
  };

  const handleToggle = () => {
    setShowArchived(prevState => !prevState);
  };

  const handleFilters = async () => {
    try {
      console.log("Filtering papers for status:", currentStatus);
      const filteredPapers = await filterByStatus(currentStatus, showArchived);
      const newPapers = filteredPapers.records;
      const newSourceIds = newPapers.map(paper => paper.source_id);

      setPapers(newPapers);
      setSourceIds(newSourceIds);
      setDisplayPapers(showOnlyItemsWithPDFs ? newPapers.filter(p => p.has_pdf) : newPapers); // Filter by PDFs if toggled on
    } catch (error) {
      console.error('Error in handleFilters:', error);
    }
  };

  // Update the displayed papers based on the PDF filter
  useEffect(() => {
    if (showOnlyItemsWithPDFs) {
      setDisplayPapers(papers.filter((paper) => paper.has_pdf)); // Assuming each paper has a `hasPDF` boolean
    } else {
      setDisplayPapers(papers); // Reset to show all papers if PDF filter is off
    }
  }, [showOnlyItemsWithPDFs, papers]);

  const clearSearch = () => {
    setSemanticSearchQuery('');
  };

  return (
    <div className={styles.container}>

      {/* Status Buttons */}
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
          </div>
        </div>

        <div className={styles.selectedAndStatusContainer}>
          <div className={styles.selectAllContainer}>
            <input
              type="checkbox"
              checked={selectAll}
              onChange={handleSelectAllChange}
            />
            <label>Select All</label>
          </div>
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
          <div className={styles.filterControlsContainer}>
            <label className={styles.filterLabel}>
              Show Archived
              <input
                type="checkbox"
                checked={showArchived}
                onChange={handleToggle}
                className={styles.toggleInput}
              />
            </label>
            <label className={styles.filterLabel}>
              Show Only Items with PDFs
              <input
                type="checkbox"
                checked={showOnlyItemsWithPDFs}
                onChange={handleToggleShowOnlyItemsWithPDFs}
                className={styles.toggleInput}
              />
            </label>
          </div>
        </div>
      </div>

      {/* Summary Box */}
      <div className={styles.summaryBox}>
        <p>{`AI Summary of items found on Page ${currentPage}.`}</p>
      </div>

      <FunnelTable
        results={displayPapers} 
        onStatusChange={handleArchiveRecord} 
        selectedPapers={selectedPapers}
        handleSelectPaper={handleSelectPaper}
        funnelStage={currentStatus}
        updateCurrentPage={updateCurrentPage} // Pass the function to update the page
        renderSummaryColumn={(paper) => (
          <>
            <div>PDF Available</div>
            {paper.has_pdf && (
              <button className={styles.pdfAssistantButton}>PDF AI Assistant</button>
            )}
          </>
        )}
      />
    </div>
  );
};

export default FunnelPage;

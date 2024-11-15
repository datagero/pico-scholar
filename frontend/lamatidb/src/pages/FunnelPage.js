import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import FunnelTable from '../components/Funnel/FunnelTable';
import styles from '../components/Funnel/Funnel.module.css';
import { filterByStatus, updateDocumentStatuses } from '../services/statusService';
import { semanticSearchQuery, fetchAISummary } from '../services/searchService'; // Adjust import if `fetchAISummary` is in `searchService.js`
import AIAssistantChat from '../components/Funnel/AIAssistantChat';

const FunnelPage = () => {
  const location = useLocation();
  const initialResults = location.state?.results || [];
  const [papers, setPapers] = useState(initialResults);
  const [sourceIds, setSourceIds] = useState(initialResults.map(paper => paper.source_id));
  const [displayIds, setDisplayPaperIds] = useState(initialResults.map(paper => paper.source_id));
  const [displayPapers, setDisplayPapers] = useState(initialResults);
  const [currentStatus, setCurrentStatus] = useState('Identified');
  const [selectedPapers, setSelectedPapers] = useState([]);
  const [semanticQuery, setSemanticSearchQuery] = useState('');
  const [selectAll, setSelectAll] = useState(false);
  const [narrowFields, setNarrowFields] = useState('All Fields');
  const [showArchived, setShowArchived] = useState(false);
  const [showOnlyItemsWithPDFs, setShowOnlyItemsWithPDFs] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [showChat, setShowChat] = useState(false);
  const [aiSummary, setAISummary] = useState(''); // Add state for AI Summary text
  const [aiSummaryTitle, setAISummaryTitle] = useState(''); // Add state for AI Summary title

  // Toggle Chat Visibility
  const toggleChat = () => {
    setShowChat(!showChat);
  };

  const updateCurrentPage = (pageNumber) => {
    setCurrentPage(pageNumber);
  };

  // Fetch AI Summary for the first 10 items on the current page
  const fetchAISummaryForPage = async () => {
    const first10Ids = sourceIds.slice(0, 10);
    try {
      const summaryText = await fetchAISummary(first10Ids);
      setAISummary(summaryText.summary);
      setAISummaryTitle(`AI Summary of First 10 Items from Page ${currentPage}`); // Update title with current page
    } catch (error) {
      console.error('Failed to fetch AI Summary:', error);
      setAISummaryTitle(`AI Summary of First 10 Items from Page ${currentPage} (Failed to load)`);
    }
  };

  useEffect(() => {
    handleFilters();
    // fetchAISummaryForPage(); // This is expensive for testing/PoC, so just load once for now
  }, [currentStatus, showArchived, currentPage]);

  const handleUpdateStatuses = async (newStage) => {
    try {
      await updateDocumentStatuses(selectedPapers, newStage);
      handleFilters();
    } catch (error) {
      console.error('Failed to update statuses:', error);
    }
  };

  const handleArchiveRecord = () => {
    handleFilters();
  };

  const handleToggleShowOnlyItemsWithPDFs = () => {
    setShowOnlyItemsWithPDFs((prevState) => !prevState);
  };

  useEffect(() => {
    const filteredPapers = displayIds
      .map(id => papers.find(paper => paper.source_id === id))
      .filter(paper => paper !== undefined);
    setDisplayPapers(filteredPapers);
  }, [displayIds, papers]);

  // Run fetchAISummaryForPage only once when the component mounts
  useEffect(() => {
    fetchAISummaryForPage();
  }, []); // Empty dependency array ensures this runs only on initial render


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
      const filteredPapers = await filterByStatus(currentStatus, showArchived);
      const newPapers = filteredPapers.records;
      const newSourceIds = newPapers.map(paper => paper.source_id);

      setPapers(newPapers);
      setSourceIds(newSourceIds);
      setDisplayPapers(showOnlyItemsWithPDFs ? newPapers.filter(p => p.has_pdf) : newPapers);
    } catch (error) {
      console.error('Error in handleFilters:', error);
    }
  };

  useEffect(() => {
    if (showOnlyItemsWithPDFs) {
      setDisplayPapers(papers.filter((paper) => paper.has_pdf));
    } else {
      setDisplayPapers(papers);
    }
  }, [showOnlyItemsWithPDFs, papers]);

  const clearSearch = () => {
    setSemanticSearchQuery('');
  };

  return (
    <div className={styles.container}>
      <div className={styles.statusButtonsContainer}>
        {['Identified', 'Screened', 'Sought Retrieval', 'Assessed Eligibility', 'Included in Review'].map((status) => (
          <button
            key={status}
            className={`${styles.statusButton} ${currentStatus === status ? styles.activeStatus : ''}`}
            onClick={() => handleStatusButtonClick(status)}
          >
            {status}
          </button>
        ))}
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
              {['Identified', 'Screened', 'Sought Retrieval', 'Assessed Eligibility', 'Included in Review'].map((stage) => (
                <option key={stage} value={stage}>{stage}</option>
              ))}
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

      {/* Summary Box with Dynamic Title */}
      <div className={styles.summaryBox}>
        <h3>{aiSummaryTitle}</h3>
        <p>{aiSummary}</p>
      </div>

      <FunnelTable
        results={displayPapers} 
        onStatusChange={handleArchiveRecord} 
        selectedPapers={selectedPapers}
        handleSelectPaper={handleSelectPaper}
        funnelStage={currentStatus}
        updateCurrentPage={updateCurrentPage}
        renderSummaryColumn={(paper) => (
          <>
            {paper.has_pdf && (
              <button
                id="pdfAiAssistantButton"
                onClick={() => toggleChat()}
                className={styles.pdfAssistantButton}
              >
                PDF AI Assistant
              </button>
            )}
          </>
        )}
      />

      {showChat && <AIAssistantChat onClose={toggleChat} />}
    </div>
  );
};

export default FunnelPage;

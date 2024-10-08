import React, { useState } from 'react';
import styles from './Funnel.module.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilePdf, faUpload } from '@fortawesome/free-solid-svg-icons';
import { updateDocumentArchivedStatus } from '../../services/statusService';

const FunnelTable = ({ results = [], selectedPapers, handleSelectPaper, onStatusChange }) => {
  const [reviewStatuses, setReviewStatuses] = useState(
    results.map(result => result.is_archived || 'No') // Initialize the review statuses
  );

  const handleReviewChange = async (index, value) => {
    const updatedStatuses = [...reviewStatuses];
    updatedStatuses[index] = value;
    setReviewStatuses(updatedStatuses);
  
    const documentId = results[index].source_id.toString();
    const isArchived = value === 'Yes';
    await updateDocumentArchivedStatus(documentId, isArchived);

    onStatusChange();
  };

  const handlePdfClick = async (documentId) => {
    try {
      const result = await startStreamlitSession(documentId);
      console.log('Streamlit session initiated:', result);
      // Additional logic to handle the session start, such as navigation or displaying a message
    } catch (error) {
      console.error('Error starting Streamlit session:', error);
      // Handle the error, such as showing a notification to the user
    }
  };
  
  

  const [currentPage, setCurrentPage] = useState(1);
  const papersPerPage = 10;

  const totalPages = Math.ceil(results.length / papersPerPage);
  const indexOfLastPaper = currentPage * papersPerPage;
  const indexOfFirstPaper = indexOfLastPaper - papersPerPage;
  const currentPapers = results.slice(indexOfFirstPaper, indexOfLastPaper);

  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  const renderPagination = () => {
    const pages = [];
    const firstPages = 5;
    const lastPages = 2;

    for (let i = 1; i <= Math.min(firstPages, totalPages); i++) {
      pages.push(
        <button
          key={i}
          onClick={() => paginate(i)}
          className={`${styles.pageLink} ${currentPage === i ? styles.activePage : ''}`}
        >
          {i}
        </button>
      );
    }

    if (totalPages > firstPages + lastPages) {
      if (currentPage > firstPages + 1) {
        pages.push(<span key="dots1">...</span>);
      }

      const startPage = Math.max(firstPages + 1, currentPage - 1);
      const endPage = Math.min(totalPages - lastPages, currentPage + 1);

      for (let i = startPage; i <= endPage; i++) {
        pages.push(
          <button
            key={i}
            onClick={() => paginate(i)}
            className={`${styles.pageLink} ${currentPage === i ? styles.activePage : ''}`}
          >
            {i}
          </button>
        );
      }

      if (currentPage < totalPages - lastPages - 1) {
        pages.push(<span key="dots2">...</span>);
      }

      for (let i = totalPages - lastPages + 1; i <= totalPages; i++) {
        pages.push(
          <button
            key={i}
            onClick={() => paginate(i)}
            className={`${styles.pageLink} ${currentPage === i ? styles.activePage : ''}`}
          >
            {i}
          </button>
        );
      }
    }

    return pages;
  };

  return (
    <div className={styles['table-container']}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={`${styles.headerCell} ${styles.headerCellSelect}`}>Select</th>
            <th className={`${styles.headerCell} ${styles.headerCellArchive}`}>Archive</th> {/* Archive column */}
            <th className={`${styles.headerCell} ${styles.headerCellSummary}`}>Summary</th>
            <th className={`${styles.headerCell} ${styles.headerCellAbstract}`}>Abstract</th>
            <th className={`${styles.headerCell} ${styles.headerCellPICO}`} title="PICO: Patient, Intervention, Comparison, Outcome">PICO</th>
            <th className={`${styles.headerCell} ${styles.headerCellStatus}`}>Status</th>
          </tr>
        </thead>
        <tbody>
          {currentPapers.map((result, index) => (
            <tr key={index} className={styles.row}>
              <td className={`${styles.cell} ${styles.selectCell}`} data-label="Select">
                <input
                  type="checkbox"
                  checked={selectedPapers.includes(result.source_id)}
                  onChange={() => handleSelectPaper(result.source_id)}
                />
              </td>
              <td className={`${styles.cell} ${styles.archiveCell}`} data-label="Archive">
                <select
                  value={result.is_archived || 'No'}
                  onChange={(e) => handleReviewChange(index, e.target.value)}
                  className={styles.reviewDropdown}
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </td>
              <td className={`${styles.cell} ${styles.summaryCell}`} data-label="Summary">
                <strong>{result.title}</strong><br />
                {result.year}, {result.authors}<br />
                ID: {result.source_id}, Similarity: {result.similarity}
                <div className={styles.iconContainer}>
                  {result.has_pdf ? (
                    <div className={styles.iconWithText}>
                      <FontAwesomeIcon icon={faFilePdf} className={styles.icon} title="PDF Available" />
                      <span>PDF Available</span>
                    </div>
                  ) : (
                    <div className={styles.iconWithText}>
                      <FontAwesomeIcon icon={faUpload} className={styles.icon} title="Upload PDF" />
                      <span>Upload PDF</span>
                    </div>
                  )}
                </div>
              </td>
              <td className={`${styles.cell} ${styles.abstractCell}`} data-label="Abstract">{result.abstract}</td>
              <td className={`${styles.cell} ${styles.picoCell}`} data-label="PICO">
                <div className={styles.picoItem} title="P (Patient) - The population or group of patients being studied">
                  <strong>P:</strong> {result.pico_p}
                </div>
                <div className={styles.picoItem} title="I (Intervention) - The intervention or treatment being considered">
                  <strong>I:</strong> {result.pico_i}
                </div>
                <div className={styles.picoItem} title="C (Comparison) - The comparison or control being used in the study">
                  <strong>C:</strong> {result.pico_c}
                </div>
                <div className={styles.picoItem} title="O (Outcome) - The outcomes being measured">
                  <strong>O:</strong> {result.pico_o}
                </div>
              </td>
              <td className={`${styles.cell} ${styles.statusCell}`} data-label="Status">{result.funnel_stage}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination Controls */}
      <div className={styles.pagination}>
        <button
          onClick={() => paginate(1)}
          disabled={currentPage === 1}
          className={styles.pageLink}
        >
          First
        </button>
        <button
          onClick={() => paginate(currentPage - 1)}
          disabled={currentPage === 1}
          className={styles.pageLink}
        >
          Previous
        </button>
        {renderPagination()}
        <button
          onClick={() => paginate(currentPage + 1)}
          disabled={currentPage === totalPages}
          className={styles.pageLink}
        >
          Next
        </button>
        <button
          onClick={() => paginate(totalPages)}
          disabled={currentPage === totalPages}
          className={styles.pageLink}
        >
          Last
        </button>
      </div>
    </div>
  );
};

export default FunnelTable;

import React, { useState } from 'react';
import styles from './Funnel.module.css';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFilePdf, faUpload } from '@fortawesome/free-solid-svg-icons';
import { updateDocumentArchivedStatus } from '../../services/statusService';

const FunnelTable = ({ results = [], selectedPapers, handleSelectPaper, onStatusChange, updateCurrentPage, renderSummaryColumn }) => {
  const [currentPage, setCurrentPage] = useState(1);
  const papersPerPage = 10;

  const paginate = (pageNumber) => {
    setCurrentPage(pageNumber);
    updateCurrentPage(pageNumber);
  };

  const totalPages = Math.ceil(results.length / papersPerPage);
  const indexOfLastPaper = currentPage * papersPerPage;
  const indexOfFirstPaper = indexOfLastPaper - papersPerPage;
  const currentPapers = results.slice(indexOfFirstPaper, indexOfLastPaper);

  const handleReviewChange = async (index, value) => {
    const documentId = results[index].source_id.toString();
    const isArchived = value === 'Yes';
    await updateDocumentArchivedStatus(documentId, isArchived);
    onStatusChange();
  };

  // Render pagination controls
  const renderPagination = () => {
    const pages = [];
    const firstPages = 2;
    const lastPages = 2;
    const surroundingPages = 2;

    // First Page button
    pages.push(
      <button
        key="first"
        onClick={() => paginate(1)}
        disabled={currentPage === 1}
        className={styles.pageLink}
      >
        First Page
      </button>
    );

    // Pages at the start
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

    // Ellipsis if there is a gap
    if (currentPage > firstPages + surroundingPages + 1) {
      pages.push(<span key="dots1">...</span>);
    }

    // Pages around the current page
    const startPage = Math.max(firstPages + 1, currentPage - surroundingPages);
    const endPage = Math.min(totalPages - lastPages, currentPage + surroundingPages);

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

    // Ellipsis if there is a gap
    if (currentPage < totalPages - lastPages - surroundingPages) {
      pages.push(<span key="dots2">...</span>);
    }

    // Pages at the end
    for (let i = Math.max(totalPages - lastPages + 1, startPage + 1); i <= totalPages; i++) {
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

    // Last Page button
    pages.push(
      <button
        key="last"
        onClick={() => paginate(totalPages)}
        disabled={currentPage === totalPages}
        className={styles.pageLink}
      >
        Last Page
      </button>
    );

    return pages;
  };

  return (
    <div className={styles['table-container']}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={`${styles.headerCell} ${styles.headerCellSelect}`}>Select</th>
            <th className={`${styles.headerCell} ${styles.headerCellArchive}`}>Archive</th>
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
                    <>
                      <div className={styles.iconWithText}>
                        <FontAwesomeIcon icon={faFilePdf} className={styles.icon} title="PDF Available" />
                        <span>PDF Available</span>
                      </div>
                      {renderSummaryColumn(result)}
                    </>
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
                <div className={styles.picoItem} title="P (Patient)">
                  <strong>P:</strong> {result.pico_p}
                </div>
                <div className={styles.picoItem} title="I (Intervention)">
                  <strong>I:</strong> {result.pico_i}
                </div>
                <div className={styles.picoItem} title="C (Comparison)">
                  <strong>C:</strong> {result.pico_c}
                </div>
                <div className={styles.picoItem} title="O (Outcome)">
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
        {renderPagination()}
      </div>
    </div>
  );
};

export default FunnelTable;

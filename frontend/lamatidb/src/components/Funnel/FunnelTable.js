import React, { useState } from 'react';
import styles from './Funnel.module.css';

const FunnelTable = ({ results = [], selectedPapers, handleSelectPaper}) => {
  const [reviewStatuses, setReviewStatuses] = useState(
    results.map(result => result.is_reviewed || 'No') // Initialize the review statuses
  );

  const handleReviewChange = (index, value) => {
    const updatedStatuses = [...reviewStatuses];
    updatedStatuses[index] = value;
    setReviewStatuses(updatedStatuses);
  };

  const [currentPage, setCurrentPage] = useState(1);
  const papersPerPage = 10;

  // Calculate the number of pages
  const totalPages = Math.ceil(results.length / papersPerPage);

  // Get the papers for the current page
  const indexOfLastPaper = currentPage * papersPerPage;
  const indexOfFirstPaper = indexOfLastPaper - papersPerPage;
  const currentPapers = results.slice(indexOfFirstPaper, indexOfLastPaper);

  // Handle page change
  const paginate = (pageNumber) => setCurrentPage(pageNumber);

  return (
    <div className={styles['table-container']}>
      <table className={styles.table}>
        <thead>
          <tr>
            <th className={styles.headerCell}>Select</th>
            <th className={styles.headerCell} style={{ width: '800px' }}>Summary</th>
            <th className={styles.headerCell} style={{ width: '500px' }}>Abstract</th>
            <th
              className={styles.headerCell}
              title="PICO: Patient, Intervention, Comparison, Outcome"
            >
              PICO
            </th>
            <th className={styles.headerCell}>Status</th>
            <th className={styles.headerCell}>Reviewed</th>
          </tr>
        </thead>
        <tbody>
          {currentPapers.map((result, index) => (
            <tr key={index} className={styles.row}>
              <td className={styles.checkboxCell} data-label="Select">
                <input
                  type="checkbox"
                  checked={selectedPapers.includes(result.source_id)}
                  onChange={() => handleSelectPaper(result.source_id)}
                />
              </td>
              <td className={`${styles.cell} ${styles.summaryCell}`} data-label="Summary">
                <strong>{result.title}</strong><br />
                {result.year}, {result.authors}<br />
                ID: {result.source_id}, Similarity: {result.similarity}
              </td>
              <td className={styles.cell} data-label="Abstract">{result.abstract}</td>
              <td className={styles.cell} data-label="PICO">
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
              <td className={styles.cell} data-label="Status">{result.funnel_stage}</td>
              <td className={styles.cell} data-label="Reviewed">
                <select
                  value={reviewStatuses[index]}
                  onChange={(e) => handleReviewChange(index, e.target.value)}
                  className={styles.reviewDropdown}
                >
                  <option value="Yes">Yes</option>
                  <option value="No">No</option>
                </select>
              </td>
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
        {Array.from({ length: totalPages }, (_, i) => (
          <button
            key={i + 1}
            onClick={() => paginate(i + 1)}
            className={`${styles.pageLink} ${currentPage === i + 1 ? styles.activePage : ''}`}
          >
            {i + 1}
          </button>
        ))}
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

// searchService.js

// The folder contains utility functions and services that handle communication with the backend API.
// Specific functions to handle search-related API requests.

export const searchQuery = async (query) => {
    try {
      const response = await fetch('/projects/1/search/', {
        method: 'POST',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query_text: query }),
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      return await response.json();
    } catch (error) {
      console.error('Error during the search request:', error);
      throw error;
    }
  };
  

  // export const updateStatus = async (Array(ID), currentStatus, updatedStatus) => {
  //   // e.g. updateStatus([16631576, 16630583], "Identified", "scoped");
  //   // Bulk Update Status in DB
  //   // Returns Updated view
  // };

  // export const getStatusRecord = async (query) => {
  //   // Bulk Update Status
  // };
  

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
  

export const semanticSearchQuery = async (query, field = "All Fields", sourceIds = []) => {
  try {
    // Ensure sourceIds is a list of strings
    sourceIds = sourceIds.map(id => String(id));

    // Construct the request payload
    const payload = {
      query: {
        query_text: query,
      },
      source_ids: sourceIds
    };

    // Make the API call to backend
    const response = await fetch('/projects/1/semantic_search/', {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
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

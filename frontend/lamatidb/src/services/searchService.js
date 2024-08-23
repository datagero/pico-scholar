// searchService.js
const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
// The folder contains utility functions and services that handle communication with the backend API.
// Specific functions to handle search-related API requests.


export const searchQuery = async (query) => {
    try {
      const response = await fetch(`${BASE_URL}/projects/1/search/`, {
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
  

export const semanticSearchQuery = async (query, fields=["All Fields"], sourceIds = []) => {
  try {
    // Ensure sourceIds is a list of strings
    sourceIds = sourceIds.map(id => String(id));

    // Construct the request payload
    const payload = {
      query: {
        query_text: query,
      },
      fields: fields,
      source_ids: sourceIds
    };

    // Make the API call to backend
    const response = await fetch(`${BASE_URL}/projects/1/semantic_search/`, {
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

export const translateTerms = async (terms) => {
  // For testing purposes, return a dummy output 
  // (e.g. you'll need this if don't have OpenAI key available)
  // const terms_output = {"scientific_notation": {
  //   "Year of Publication": "",
  //   "Country of Publication": "United States",
  //   "Does the Study use Randomized Trial?": "Yes",
  //   "P (Population)": "Adults over 25 years",
  //   "I (Intervention)": "Drug A",
  //   "C (Comparison)": "Placebo",
  //   "O (Outcome)": "Reduction in symptoms"
  // }};
  // return terms_output;

  try {
    // Construct the request payload
    const payload = terms;

    // Make the API call to the backend translation service
    const response = await fetch(`${BASE_URL}/translate_terms/`, {
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
    console.error('Error during the translation request:', error);
    throw error;
  }
};
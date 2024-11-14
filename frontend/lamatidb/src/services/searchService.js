const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

// Fetch AI summary for first 10 items
export const fetchAISummary = async (itemIds) => {
  try {
    const response = await fetch(`${BASE_URL}/summary/ai_summary/`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ item_ids: itemIds }),
    });

    if (!response.ok) {
      throw new Error('Network response was not ok');
    }

    const data = await response.json();
    return data.summaryText; // Adjust based on your API's response format
  } catch (error) {
    console.error('Error fetching AI summary:', error);
    return 'Failed to load AI summary.';
  }
};

// Function to execute a simple search query
export const searchQuery = async (query) => {
  try {
    const response = await fetch(`${BASE_URL}/search/projects/1/simple_search/`, {
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

// Function for performing a semantic search
export const semanticSearchQuery = async (query, fields = ["All Fields"], sourceIds = []) => {
  try {
    sourceIds = sourceIds.map(id => String(id));

    const payload = {
      query: {
        query_text: query,
      },
      fields: fields,
      source_ids: sourceIds,
    };

    const response = await fetch(`${BASE_URL}/search/projects/1/semantic_search/`, {
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

// Function to translate terms for use in other contexts or displays
export const translateTerms = async (terms) => {
  try {
    const payload = terms;

    const response = await fetch(`${BASE_URL}/search/translate_terms/`, {
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

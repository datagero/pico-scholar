// searchService.js

// The folder contains utility functions and services that handle communication with the backend API.
// Specific functions to handle search-related API requests.

// searchService.js

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

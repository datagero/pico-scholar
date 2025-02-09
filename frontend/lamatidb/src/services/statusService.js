const BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
export const filterByStatus = async (currentStatus, show_archived = false) => {
  try {
      // Construct the query string with the archived parameter
      const queryParams = new URLSearchParams({
        archived: show_archived.toString()  // Convert the boolean to a string ('true' or 'false')
      });

      const response = await fetch(`${BASE_URL}/search/projects/1/get_status/${currentStatus}?${queryParams.toString()}`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        }
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

export const updateDocumentStatuses = async (documentIds, newStatus) => {
  try {
    const response = await fetch(`${BASE_URL}/search/projects/1/documents/${documentIds.join(',')}/status/${newStatus}`, {
      method: 'PATCH',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to update document statuses');
    }

    const result = await response.json();
    console.log('Status update successful:', result);
    return result;
  } catch (error) {
    console.error('Error updating document statuses:', error);
    throw error;
  }
};

export const updateDocumentArchivedStatus = async (documentId, isArchived) => {
  try {
    const response = await fetch(`${BASE_URL}/search/projects/1/document/${documentId.toString()}/archive/${isArchived}`, {
      method: 'PATCH',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to update document archived status');
    }

    const result = await response.json();
    console.log('Archived status update successful:', result);
    return result;
  } catch (error) {
    console.error('Error updating document archived status:', error);
    throw error;
  }
};

export const startStreamlitSession = async (documentId) => {
  try {
    const response = await fetch(`${BASE_URL}/projects/1/chat/document/${documentId.toString()}`, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error('Failed to start Streamlit session');
    }

    const result = await response.json();
    console.log('Streamlit session started successfully:', result);
    return result;
  } catch (error) {
    console.error('Error starting Streamlit session:', error);
    throw error;
  }
};

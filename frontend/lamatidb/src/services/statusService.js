
  // export const updateStatus = async (Array(ID), currentStatus, updatedStatus) => {
  //   // e.g. updateStatus([16631576, 16630583], "Identified", "scoped");
  //   // Bulk Update Status in DB
  //   // Returns Updated view
  // };

export const filterByStatus = async (currentStatus) => {
  try {
      const response = await fetch(`/projects/1/get_status/${currentStatus}`, {
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
    const response = await fetch(`/projects/1/documents/${documentIds.join(',')}/status/${newStatus}`, {
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

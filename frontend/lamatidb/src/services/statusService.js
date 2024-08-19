
  // export const updateStatus = async (Array(ID), currentStatus, updatedStatus) => {
  //   // e.g. updateStatus([16631576, 16630583], "Identified", "scoped");
  //   // Bulk Update Status in DB
  //   // Returns Updated view
  // };

  export const filterByStatus = async (currentStatus) => {
    try {
        const response = await fetch('/projects/1/search/', {
          method: 'POST',
          headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ status: currentStatus }),
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
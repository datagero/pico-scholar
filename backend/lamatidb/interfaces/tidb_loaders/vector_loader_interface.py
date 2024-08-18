from llama_index.core import Document
from lamatidb.interfaces.mysql_interface import MySQLInterface

class LoaderInterface:
    """
    Base loader interface for reading and processing data.
    Loaders return Document objects for LlamaIndex.
    """
    
    def __init__(self):
        """
        Initialize the LoaderInterface with a database connection.
        
        :param database_name: The name of the MySQL database to connect to.
        """
        self.mysql_interface = MySQLInterface()
        self.mysql_interface.setup_database()
        self.engine = self.mysql_interface.engine
        self.raw_data = None
        self.documents = None  # List of Document objects for LlamaIndex

class LoaderPubMedMySQL(LoaderInterface):
    """Loader class for fetching and processing PubMed data from MySQL."""
    
    def __init__(self):
        """
        Initialize LoaderPubMedMySQL with a specific database.
        
        :param database_name: The name of the MySQL database to connect to.
        """
        super().__init__()
        self.sample_dict = None
        self.sample_text = None

    def load_data(self):
        """Load PubMed data from the MySQL database."""
        query = """
        SELECT Document.documentId, title, author, abstract, `year`
        FROM Document
        INNER JOIN DocumentAbstract ON Document.documentId = DocumentAbstract.documentId;
        """
        self.raw_data = self.mysql_interface.fetch_data_from_db(query)

    def process_data(self):
        """
        Process and clean PubMed data to create Document objects for LlamaIndex.
        
        The process involves:
        - Filtering out rows with empty abstracts.
        - Creating a dictionary and list of documents based on the processed data.
        """
        
        def ignore_empty_abstract():
            """
            Filter out records without an abstract.
            
            :return: Filtered list of rows.
            """
            content = [x for x in self.raw_data if x[3] != '' and x[3] is not None]
            return content

        # Process and clean PubMed data
        content = ignore_empty_abstract()

        # Convert the processed data into a dictionary and prepare text samples
        self.sample_dict = {x[0]: {'text': x[3], 'title': x[1], 'authors': x[2], 'year': x[4]} for x in content}
        self.sample_text = [x['text'] for x in self.sample_dict.values()]

        # Create LlamaIndex Document objects
        self.documents = [
            Document(
                text=values['text'],
                metadata={
                    "source": doc_id,
                    "title": values['title'],
                    "authors": values['authors'],
                    "year": values['year']
                },
            )
            for doc_id, values in self.sample_dict.items()
        ]

    def get_documents(self):
        """
        Retrieve the processed Document objects.
        
        :return: List of Document objects.
        """
        return self.documents

if __name__ == "__main__":
    # Initialize the loader with your database name
    loader = LoaderPubMedMySQL()

    # Load and process the data
    print("Loading data from MySQL database...")
    loader.load_data()
    print("Data loaded successfully.")

    print("Processing data...")
    loader.process_data()
    print("Data processed successfully.")

    # Retrieve the documents to feed into LlamaIndex
    documents = loader.get_documents()

    # Print out some details about the loaded documents for verification
    if documents:
        print(f"Total documents loaded: {len(documents)}")
        print("Sample document:")
        print(f"Title: {documents[0].metadata['title']}")
        print(f"Authors: {documents[0].metadata['authors']}")
        print(f"Year: {documents[0].metadata['year']}")
        print(f"Text: {documents[0].text[:500]}...")  # Print the first 500 characters of the text
    else:
        print("No documents found.")
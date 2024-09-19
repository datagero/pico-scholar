from llama_index.core import Document
from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface
import itertools

class LoaderInterface:
    """
    Base loader interface for reading and processing data.
    Loaders return Document objects for LlamaIndex.
    """
    
    def __init__(self, db_type, db_name):
        """
        Initialize the LoaderInterface with a database connection.
        
        :param database_name: The name of the MySQL database to connect to.
        """
        self.mysql_interface = DatabaseInterface(db_type=db_type, db_name=db_name)
        # self.mysql_interface = DatabaseInterface()
        self.mysql_interface.setup_database()
        self.engine = self.mysql_interface.engine
        self.raw_data = None
        self.documents = None  # List of Document objects for LlamaIndex

    def get_documents(self):
        """
        Retrieve the processed Document objects.
        
        :return: List of Document objects.
        """
        return self.documents

class LoaderPubMedAbstracts(LoaderInterface):
    """Loader class for fetching and processing PubMed data from MySQL."""
    
    def __init__(self, db_type='tidb', db_name='test_creation'):
        """
        Initialize LoaderPubMedAbstracts with a specific database.
        
        :param database_name: The name of the MySQL database to connect to.
        """
        super().__init__(db_type=db_type, db_name=db_name)
        self.sample_dict = None
        self.sample_text = None

    def load_data(self):
        """Load PubMed data from the MySQL database."""
        # query = """
        # SELECT Document.documentId, title, author, abstract, `year`
        # FROM Document
        # INNER JOIN DocumentAbstract ON Document.documentId = DocumentAbstract.documentId;
        # """

        query = """
        SELECT 
            Document.documentId, 
            title, 
            author, 
            abstract, 
            `year`,
            pico_p,
            pico_i,
            pico_c,
            pico_o
        FROM Document
        INNER JOIN DocumentAbstract ON Document.documentId = DocumentAbstract.documentId
        LEFT JOIN DocumentPICO_enhanced ON Document.documentId = DocumentPICO_enhanced.documentId;
        """

        self.raw_data = self.mysql_interface.fetch_data_from_db(query)

    def clean_data(self):

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
        self.sample_dict = {x[0]: {'text': x[3], 'title': x[1], 'authors': x[2], 'year': x[4], 
                                   'pico_p': x[5], 'pico_i': x[6], 'pico_c': x[7], 'pico_o': x[8]} for x in content}
        self.sample_text = [x['text'] for x in self.sample_dict.values()]


    def process_data(self):
        """
        Process and clean PubMed data to create Document objects for LlamaIndex.
        
        The process involves:
        - Filtering out rows with empty abstracts.
        - Creating a dictionary and list of documents based on the processed data.
        """
        
        self.clean_data() # initialise self.sample_dict

        # Create LlamaIndex Document objects
        self.documents = [
            Document(
                text=values['text'],
                metadata={
                    "source": doc_id,
                    "title": values['title'],
                    "authors": values['authors'],
                    "year": values['year'],
                    'pico_p': values['pico_p'],
                    'pico_i': values['pico_i'],
                    'pico_c': values['pico_c'],
                    'pico_o': values['pico_o']
                },
            )
            for doc_id, values in self.sample_dict.items()
        ]


class LoaderPubMedPICO(LoaderPubMedAbstracts):
    """Loader class for fetching and processing PubMed data from MySQL."""
    
    def __init__(self, db_type='tidb', db_name='test_creation'):
        """
        Initialize LoaderPubMedAbstracts with a specific database.
        
        :param database_name: The name of the MySQL database to connect to.
        """
        super().__init__(db_type=db_type, db_name=db_name)
        self.sample_dict = None
        self.sample_text = None

    def recover_final_picos_from_vector_db(self):
        """ 
        This is recovery code in case of operational db deletion
        Since currently generating PICOs require OpenAI key, it is costly and time-consuming.
        The class will have to be initialised with the vector database.
        """

        query = """
        SELECT 
            JSON_UNQUOTE(JSON_EXTRACT(meta, '$.source')) AS documentId,
            JSON_UNQUOTE(JSON_EXTRACT(meta, '$.pico_p')) AS pico_p,
            JSON_UNQUOTE(JSON_EXTRACT(meta, '$.pico_i')) AS pico_i,
            JSON_UNQUOTE(JSON_EXTRACT(meta, '$.pico_c')) AS pico_c,
            JSON_UNQUOTE(JSON_EXTRACT(meta, '$.pico_o')) AS pico_o
        FROM 
            scibert_alldata_pico.scibert_alldata;
        """
        import json
        recovered_data = self.mysql_interface.fetch_data_from_db(query)
        keys = ['documentId', 'pico_p', 'pico_i', 'pico_c', 'pico_o']

        
        # Create a dictionary from the tuple
        data_dicts = [dict(zip(keys, entry)) for entry in recovered_data]

        # Convert the dictionary to JSON
        json_data = json.dumps(data_dicts, indent=4)

        # Save the JSON to a file
        with open('datalake/pubmed/recovered_pico_data.json', 'w') as json_file:
            json_file.write(json_data)

    def load_data(self):
        """Load PubMed data from the MySQL database: Only those with PICO values"""
        # query = """
        # SELECT Document.documentId, title, author, abstract, `year`
        # FROM Document
        # INNER JOIN DocumentAbstract ON Document.documentId = DocumentAbstract.documentId;
        # """

        query = """
        SELECT 
            Document.documentId, 
            title, 
            author, 
            abstract, 
            `year`,
            COALESCE(pico_p, '') AS pico_p,
            COALESCE(pico_i, '') AS pico_i,
            COALESCE(pico_c, '') AS pico_c,
            COALESCE(pico_o, '') AS pico_o
        FROM Document
        INNER JOIN DocumentAbstract ON Document.documentId = DocumentAbstract.documentId
        INNER JOIN DocumentPICO_enhanced ON Document.documentId = DocumentPICO_enhanced.documentId;
        """

        self.raw_data = self.mysql_interface.fetch_data_from_db(query)

    def process_data(self):
        """
        Process and clean PubMed data to create Document objects for LlamaIndex.
        
        The process involves:
        - Filtering out rows with empty abstracts.
        - Creating a dictionary and list of documents based on the processed data.
        """
        
        self.clean_data() # initialise self.sample_dict

        # Define your columns
        columns = ['pico_p', 'pico_i', 'pico_c', 'pico_o']

        # Generate all combinations of the columns
        combinations = []
        for r in range(1, len(columns) + 1):
            combinations += list(itertools.combinations(columns, r))

        self.documents_dict = {}

        # For each combination, generate a document with the concatenated values and metadata of doc_id
        for combination in combinations:
            index = "".join([x.split("_")[-1] for x in combination])
            # Create LlamaIndex Document objects
            self.documents_dict[index] = [
                Document(
                    text=" ".join([values[col] for col in combination]),
                    metadata={
                        "source": doc_id
                    },
                )
                for doc_id, values in self.sample_dict.items()
            ]

    def get_documents_dict(self):
        """
        Retrieve the processed Document objects.
        
        :return: List of Document objects.
        """
        return self.documents_dict

class LoaderPubMedFullText(LoaderInterface):
    
    def load_data(self):
        """Load PubMed data from the MySQL database."""
        # query = """
        # SELECT Document.documentId, title, author, abstract, `year`
        # FROM Document
        # INNER JOIN DocumentAbstract ON Document.documentId = DocumentAbstract.documentId;
        # """

        query = """
        SELECT 
            documentId, 
            PMCID, 
            `fullText`
        FROM DocumentFull
        """

        self.raw_data = self.mysql_interface.fetch_data_from_db(query)


    def clean_data(self):
            
        # From blob convert to text
        def blob_to_text(blob):
            return blob.decode('utf-8')
        
        clean_data = [(x[0], x[1], x[2]) for x in self.raw_data]

        # Convert the processed data into a dictionary and prepare text samples
        self.sample_dict = {x[0]: {'text': x[2], 'PMCID': x[1]} for x in clean_data}
        self.sample_text = [x['text'] for x in self.sample_dict.values()]

    def process_data(self):
        """
        Process and clean PubMed data to create Document objects for LlamaIndex.
        
        The process involves:
        - Filtering out rows with empty abstracts.
        - Creating a dictionary and list of documents based on the processed data.
        """
        
        self.clean_data() # initialise self.sample_dict

        # Create LlamaIndex Document objects
        self.documents = [
            Document(
                text=values['text'],
                metadata={
                    "source": doc_id,
                    "PMCID": values['PMCID']
                },
            )
            for doc_id, values in self.sample_dict.items()
        ]


if __name__ == "__main__":
    # Initialize the loader with your database name
    loader = LoaderPubMedAbstracts()

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
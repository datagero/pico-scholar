import csv
from llama_index.core import Document

class LoaderInterface:
    def __init__(self, path):
        self.path = path
        self.raw_data = None
        self.documents = None # List of Document objects for LlamaIndex
        
    def read_csv(self, file_path):
        data = []
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                data.append(row)
        return data

class LoaderPubMedCSV(LoaderInterface):
    def __init__(self, csv_path: str):
        # initialise parent
        super().__init__(csv_path)
        self.sample_dict = None
        self.sample_text = None

    def load_data(self):
        self.raw_data = self.read_csv(self.path)

    def process_data(self):
        # We define some helper functions and then select most suitable according to tests / use-case
        def fill_empty_abstract():
            # If abstract is empty, then fill it with title
            content = self.raw_data[:]
            for row in content:
                if row[3] == '':
                    row[3] = row[1]
            return content

        def ignore_empty_abstract():
            # To get better quality results, let's ignore the records without abstract
            content = [x for x in self.raw_data if x[3] != '']
            return content

        # Process and clean PubMed data
        content = ignore_empty_abstract()

        self.sample_dict = {x[0]: {'text' : x[3], 'title': x[1], 'authors': x[2], 'year': x[4]} for x in content[1:]}
        self.sample_text = [x['text'] for x in self.sample_dict.values()]


        self.documents = [
            Document(
                text=values['text'],
                metadata={"source": doc_id,
                        "title": values['title'],
                        "authors": values['authors'],
                        "year": values['year']},
            )
            for doc_id, values in self.sample_dict.items()
        ]

    def get_documents(self):
        return self.documents

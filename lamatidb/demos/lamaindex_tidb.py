import os

import click
from sqlalchemy import URL
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.vector_stores.tidbvector import TiDBVectorStore # type: ignore
from llama_index.readers.web import SimpleWebPageReader


tidb_connection_url = URL(
    "mysql+pymysql",
    username=os.environ['TIDB_USERNAME'],
    password=os.environ['TIDB_PASSWORD'],
    host=os.environ['TIDB_HOST'],
    port=4000,
    database="test",
    query={"ssl_verify_cert": True, "ssl_verify_identity": True},
)
tidbvec = TiDBVectorStore(
    connection_string=tidb_connection_url,
    table_name="llama_index_rag_test",
    distance_strategy="cosine",
    vector_dimension=1536, # The dimension is decided by the model
    drop_existing_table=False,
)
tidb_vec_index = VectorStoreIndex.from_vector_store(tidbvec)
storage_context = StorageContext.from_defaults(vector_store=tidbvec)
query_engine = tidb_vec_index.as_query_engine(streaming=True)


def do_prepare_data(url):
    documents = SimpleWebPageReader(html_to_text=True).load_data([url,])
    tidb_vec_index.from_documents(documents, storage_context=storage_context, show_progress=True)


_default_url = 'https://docs.pingcap.com/tidb/stable/overview'

@click.command()
@click.option('--url',default=_default_url,
              help=f'URL you want to talk to, default={_default_url}')
def chat_with_url(url):
    do_prepare_data(url)
    while True:
        question = click.prompt("Enter your question")
        response = query_engine.query(question)
        click.echo(response)

if __name__ == '__main__':
    chat_with_url()
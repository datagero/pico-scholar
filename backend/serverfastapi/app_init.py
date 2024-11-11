import itertools
import concurrent.futures
from sqlalchemy.orm import sessionmaker
from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.settings_manager import SettingsManager

def initialize_services():
    """Initialize all services and resources."""
    # Set global application settings
    SettingsManager.set_global_settings()

    # Initialize databases and engines
    operations_db = DatabaseInterface(db_type='mysql', db_name='operations_test', force_recreate_db=True)
    operations_db.setup_database()
    datastore_db = DatabaseInterface(db_type='tidb', db_name='datastore')

    # Create engine and session maker
    engine = operations_db.engine
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # index, index_fulltext, metadata_indexes, index_metadata_keys = None, None, None, None

    # Database and vector table names
    DB_NAME = "scibert_alldata_pico"
    VECTOR_TABLE_NAME = 'scibert_alldata'

    # Load indexes using the operations database
    index = _load_index("scibert_synergy", DB_NAME)
    index_fulltext = _load_index(f'{VECTOR_TABLE_NAME}_fulltext', DB_NAME)

    # Load PICO indexes in parallel
    metadata_indexes, index_metadata_keys = _load_pico_indexes(VECTOR_TABLE_NAME, DB_NAME)

    return {
        "engine": engine,
        "SessionLocal": SessionLocal,
        "index": index,
        "index_fulltext": index_fulltext,
        "metadata_indexes": metadata_indexes,
        "index_metadata_keys": index_metadata_keys,
        "datastore_db": datastore_db
    }

def _load_index(table_name, db_name):
    """Helper function to load a single index."""
    idx_interface = IndexInterface(db_name, table_name)
    idx_interface.load_index_from_vector_store()
    return idx_interface.get_index()

def _load_pico_indexes(base_table_name, db_name):
    """Load all PICO metadata indexes in parallel."""
    elements = ['p', 'i', 'c', 'o']
    combinations = [comb for r in range(1, len(elements) + 1) 
                    for comb in itertools.combinations(elements, r)]

    metadata_indexes = {}
    index_metadata_keys = []

    def load_index(combination):
        key = ''.join(combination)
        # Pass the correct database object
        return key, _load_index(f"{base_table_name}_{key}", db_name)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {executor.submit(load_index, comb): comb for comb in combinations}
        for future in concurrent.futures.as_completed(futures):
            key, index = future.result()
            metadata_indexes[key] = index
            index_metadata_keys.append(key)

    return metadata_indexes, index_metadata_keys


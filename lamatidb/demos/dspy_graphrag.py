# From https://github.com/pingcap/tidb-vector-python/blob/main/examples/graphrag-step-by-step-tutorial/example.ipynb
# Note, this uses dspy

import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

import pymysql
import dspy
import enum
import openai

from pymysql import Connection
from pymysql.cursors import DictCursor
from dspy.functional import TypedPredictor
from pydantic import BaseModel, Field
from typing import Mapping, Any, Optional, List
from langchain_community.document_loaders import WikipediaLoader
from pyvis.network import Network
from IPython.display import HTML

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    JSON,
    ForeignKey,
    BLOB,
    Enum as SQLEnum,
    DateTime,
    URL,
    create_engine,
    or_,
)
from sqlalchemy.orm import relationship, Session, declarative_base, joinedload
from tidb_vector.sqlalchemy import VectorType


# DSPy Part

class Entity(BaseModel):
    """List of entities extracted from the text to form the knowledge graph"""

    name: str = Field(
        description="Name of the entity, it should be a clear and concise term"
    )
    description: str = Field(
        description=(
            "Description of the entity, it should be a complete and comprehensive sentence, not few words. "
            "Sample description of entity 'TiDB in-place upgrade': "
            "'Upgrade TiDB component binary files to achieve upgrade, generally use rolling upgrade method'"
        )
    )


class Relationship(BaseModel):
    """List of relationships extracted from the text to form the knowledge graph"""

    source_entity: str = Field(
        description="Source entity name of the relationship, it should an existing entity in the Entity list"
    )
    target_entity: str = Field(
        description="Target entity name of the relationship, it should an existing entity in the Entity list"
    )
    relationship_desc: str = Field(
        description=(
            "Description of the relationship, it should be a complete and comprehensive sentence, not few words. "
            "Sample relationship description: 'TiDB will release a new LTS version every 6 months.'"
        )
    )

class KnowledgeGraph(BaseModel):
    """Graph representation of the knowledge for text."""

    entities: List[Entity] = Field(
        description="List of entities in the knowledge graph"
    )
    relationships: List[Relationship] = Field(
        description="List of relationships in the knowledge graph"
    )

class ExtractGraphTriplet(dspy.Signature):
    """Carefully analyze the provided text from database documentation and community blogs to thoroughly identify all entities related to database technologies, including both general concepts and specific details.

    Follow these Step-by-Step Analysis:

    1. Extract Meaningful Entities:
      - Identify all significant nouns, proper nouns, and technical terminologies that represent database-related concepts, objects, components, features, issues, key steps, execute order, user case, locations, versions, or any substantial entities.
      - Ensure that you capture entities across different levels of detail, from high-level overviews to specific technical specifications, to create a comprehensive representation of the subject matter.
      - Choose names for entities that are specific enough to indicate their meaning without additional context, avoiding overly generic terms.
      - Consolidate similar entities to avoid redundancy, ensuring each represents a distinct concept at appropriate granularity levels.

    2. Establish Relationships:
      - Carefully examine the text to identify all relationships between clearly-related entities, ensuring each relationship is correctly captured with accurate details about the interactions.
      - Analyze the context and interactions between the identified entities to determine how they are interconnected, focusing on actions, associations, dependencies, or similarities.
      - Clearly define the relationships, ensuring accurate directionality that reflects the logical or functional dependencies among entities. \
         This means identifying which entity is the source, which is the target, and what the nature of their relationship is (e.g., target_entity for $relationship).

    Some key points to consider:
      - Please endeavor to extract all meaningful entities and relationships from the text, avoid subsequent additional gleanings.

    Objective: Produce a detailed and comprehensive knowledge graph that captures the full spectrum of entities mentioned in the text, along with their interrelations, reflecting both broad concepts and intricate details specific to the database domain.

    """

    text = dspy.InputField(
        desc="a paragraph of text to extract entities and relationships to form a knowledge graph"
    )
    knowledge: KnowledgeGraph = dspy.OutputField(
        desc="Graph representation of the knowledge extracted from the text."
    )


class Extractor(dspy.Module):
    def __init__(self):
        super().__init__()
        self.prog_graph = TypedPredictor(ExtractGraphTriplet)

    def forward(self, text):
        return self.prog_graph(
            text=text,
            config={
                "response_format": {"type": "json_object"},
            },
        )

def jupyter_interactive_graph(kg: KnowledgeGraph) -> str:
    net = Network(notebook=True, cdn_resources='remote')

    node_map = {}
    for index in range(len(kg.entities)):
        node_map[kg.entities[index].name] = index
        net.add_node(
            index,
            label=kg.entities[index].name,
            title=kg.entities[index].description
        )

    for index in range(len(kg.relationships)):
        relation = kg.relationships[index]
        src_index = node_map[relation.source_entity]
        target_index = node_map[relation.target_entity]
        net.add_edge(src_index, target_index)

    filename = "kg.html"
    net.save_graph(filename)

    return filename


# OpenAI Part

def get_query_embedding(query: str):
    open_ai_client = openai.OpenAI(api_key=api_key)
    response = open_ai_client.embeddings.create(input=[query], model="text-embedding-3-small")
    return response.data[0].embedding


def generate_result(query: str, entities, relationships):
    open_ai_client = openai.OpenAI(api_key=api_key)
    entities_prompt = '\n'.join(map(lambda e: f'(Name: "{e.name}", Description: "{e.description}")', entities))
    relationships_prompt = '\n'.join(map(lambda r: f'"{r.relationship_desc}"', relationships))

    response = open_ai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Please carefully think the user's " +
             "question and ONLY use the content below to generate answer:\n" +
             f"Entities: {entities_prompt}, Relationships: {relationships_prompt}"},
            {"role": "user", "content": query}
        ])

    return response.choices[0].message.content


# TiDB Serverless Database Part

def get_db_url():
    return URL(
        drivername="mysql+pymysql",
        username=os.getenv("TIDB_USER"),
        password=os.getenv("TIDB_PASSWORD"),
        host=os.getenv('TIDB_HOST'),
        port=int(os.getenv("TIDB_PORT")),
        database=os.getenv("TIDB_DB_NAME"),
        query={"ssl_verify_cert": True, "ssl_verify_identity": True},
    )

engine = create_engine(get_db_url(), pool_recycle=300)
Base = declarative_base()

class DatabaseEntity(Base):
    id = Column(Integer, primary_key=True)
    name = Column(String(512))
    description = Column(Text)
    description_vec = Column(VectorType())

    __tablename__ = "entities"


class DatabaseRelationship(Base):
    id = Column(Integer, primary_key=True)
    source_entity_id = Column(Integer, ForeignKey("entities.id"))
    target_entity_id = Column(Integer, ForeignKey("entities.id"))
    relationship_desc = Column(Text)

    source_entity = relationship("DatabaseEntity", foreign_keys=[source_entity_id])
    target_entity = relationship("DatabaseEntity", foreign_keys=[target_entity_id])

    __tablename__ = "relationships"

def save_knowledge_graph(kg: KnowledgeGraph):
    data_entities = list(map(lambda e: DatabaseEntity(
        name = e.name,
        description = e.description,
        description_vec = get_query_embedding(e.description)
    ), kg.entities))

    with Session(engine) as session:
        session.add_all(data_entities)
        # get increment ids
        session.flush()

        entity_id_map = dict(map(lambda e: (e.name, e.id), data_entities))
        data_relationships = list(map(lambda r: DatabaseRelationship(
            source_entity_id = entity_id_map[r.source_entity],
            target_entity_id = entity_id_map[r.target_entity],
            relationship_desc = r.relationship_desc
        ), kg.relationships))

        session.add_all(data_relationships)
        session.commit()

def retrieve_entities_relationships(question_embedding) -> (List[DatabaseEntity], List[DatabaseRelationship]) :
    with Session(engine) as session:
        entity = session.query(DatabaseEntity) \
            .order_by(DatabaseEntity.description_vec.cosine_distance(question_embedding)) \
            .limit(1).first()
        entities = {entity.id: entity}

        relationships = session.query(DatabaseRelationship).options(
            joinedload(DatabaseRelationship.source_entity),
            joinedload(DatabaseRelationship.target_entity),
        ).filter(
            or_(
                DatabaseRelationship.source_entity == entity,
                DatabaseRelationship.target_entity == entity
            )
        )

        for r in relationships:
            entities.update({
                r.source_entity.id: r.source_entity,
                r.target_entity.id: r.target_entity,
            })

        return entities.values(), relationships

# Initial

extractor = Extractor()
Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)



# PART 1: INDEXING
open_ai_client = dspy.OpenAI(model="gpt-4o", api_key=api_key, max_tokens=4096)
dspy.settings.configure(lm=open_ai_client)

# Load Raw Wikipedia Page
wiki = WikipediaLoader(query="Elon Musk").load()
pred = extractor(text = wiki[0].page_content)
HTML(filename=jupyter_interactive_graph(pred.knowledge))
save_knowledge_graph(pred.knowledge)


# PART 2: RETRIEVE
question = "Who is Elon Musk?" # @param {type:"string"}

#Find Entites and Relationships
question_embedding = get_query_embedding(question)

entities, relationships = retrieve_entities_relationships(question_embedding)
# PART 3. Generate Answer
result = generate_result(question, entities, relationships)
result
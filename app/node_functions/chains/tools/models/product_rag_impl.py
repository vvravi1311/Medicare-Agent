from   dotenv import load_dotenv
load_dotenv()

from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

# project internal imports
from app.node_functions.chains.tools.models.constants import LAST,FIRST,EMBEDDING_MODEL,PRODUCT_VECTOR_INDEX_NAME,K

# Initialize embeddings (same as ingestion.py)
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL
)

#Initialize vector store
vectorstore = PineconeVectorStore(
    index_name=PRODUCT_VECTOR_INDEX_NAME, embedding=embeddings
)

# @tool(response_format="content_and_artifact")
def retrieve_product_context(query: str):
    """Retrieve relevant documentation to help answer answers Insurance agents' queries about Real-Time clause and Benefit lookup."""
    # Retrieve top 4 most similar documents
    retrieved_docs = vectorstore.as_retriever().invoke(query, k=K)

    # Serialize documents for the model
    serialized = "\n\n".join(
        (f"Source: {doc.metadata.get('source', 'Unknown')}\n\nContent: {doc.page_content}")
        for doc in retrieved_docs
    )
    # Return both serialized content and raw documents
    return serialized, retrieved_docs
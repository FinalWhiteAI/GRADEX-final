# services.py
import os
import uuid
from typing import List, Dict, Any, Tuple
from dotenv import load_dotenv
from fastapi import HTTPException
from fastapi.concurrency import run_in_threadpool
from qdrant_client import QdrantClient, models
from sentence_transformers import SentenceTransformer, CrossEncoder

# --- Core LangChain Imports ---
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# --- ADDED: Imports for Conversational RAG ---
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI# Or your preferred LLM
# --- END ADDED ---
from dotenv import load_dotenv
load_dotenv()
import config

# --- 1. Initialize Models and Clients (Loaded once on startup) ---
try:
    print(f"Loading embedding model: {config.EMBEDDING_MODEL_NAME}...")
    model = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    print("Embedding model loaded successfully.")

    print("Loading reranker model: cross-encoder/ms-marco-MiniLM-L-6-v2...")
    rerank_model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    print("Reranker model loaded.")

    # --- ADDED: Initialize the LLM ---
    print("Loading LLM (gemini 2.5 flash lite)...")
    # (Make sure OPENAI_API_KEY is set in your environment variables)
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)
    print("LLM loaded.")
    # --- END ADDED ---

except Exception as e:
    print(f"Error loading models: {e}")
    raise

try:
    print(f"Connecting to Qdrant at {config.QDRANT_HOST}:{config.QDRANT_PORT}...")
    client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)
    print("Qdrant client connected.")
except Exception as e:
    print(f"Error connecting to Qdrant: {e}")
    raise

def initialize_database():
    """Ensures the Qdrant collection and payload indexes exist."""
    try:
        client.get_collection(collection_name=config.COLLECTION_NAME)
        print(f"Collection '{config.COLLECTION_NAME}' already exists.")
    except Exception:
        print(f"Collection '{config.COLLECTION_NAME}' not found. Creating...")
        client.recreate_collection(
            collection_name=config.COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=config.EMBEDDING_DIM,
                distance=models.Distance.COSINE
            ),
        )
        print(f"Collection '{config.COLLECTION_NAME}' created.")
        print("Creating payload indexes...")
        client.create_payload_index(
            collection_name=config.COLLECTION_NAME,
            field_name="user_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        client.create_payload_index(
            collection_name=config.COLLECTION_NAME,
            field_name="document_id",
            field_schema=models.PayloadSchemaType.KEYWORD
        )
        print("Payload indexes created for 'user_id' and 'document_id'.")


def load_and_split_document(temp_file_path: str, file_name: str) -> List[Document]:
    file_extension = os.path.splitext(file_name)[1].lower()

    if file_extension == ".pdf":
        loader = PyPDFLoader(temp_file_path)
    elif file_extension == ".docx":
        loader = Docx2txtLoader(temp_file_path)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_extension}. Please upload PDF or DOCX."
        )
    
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP
    )
    chunks = text_splitter.split_documents(documents)
    
    if not chunks:
        raise HTTPException(status_code=400, detail="No text content found in the document.")
    return chunks

async def embed_and_store_chunks(chunks: List[Document], user_id: str, file_name: str) -> Tuple[int, str]:
    document_id = str(uuid.uuid4())
    points_to_upload = []
    
    texts_to_embed = ["passage: " + chunk.page_content for chunk in chunks]
    
    print(f"Embedding {len(texts_to_embed)} chunks in a thread pool...")
    vectors = await run_in_threadpool(model.encode, texts_to_embed)
    print("Embedding complete.")
    
    for i, chunk in enumerate(chunks):
        points_to_upload.append(
            models.PointStruct(
                id=str(uuid.uuid4()),
                vector=vectors[i].tolist(),
                payload={
                    "user_id": user_id,
                    "document_id": document_id,
                    "file_name": file_name,
                    "text": chunk.page_content,
                    "page_number": chunk.metadata.get("page", 0)
                }
            )
        )

    if points_to_upload:
        await run_in_threadpool(
            client.upsert,
            collection_name=config.COLLECTION_NAME,
            points=points_to_upload,
            wait=True
        )
    
    return len(points_to_upload), document_id

async def search_documents(user_id: str, document_id: str, query: str) -> List[Dict[str, Any]]:
    """
    Searches Qdrant, then reranks the results for maximum relevance.
    """
    
    prefixed_query = "query: " + query
    
    query_vector = await run_in_threadpool(model.encode, prefixed_query)

    search_results = await run_in_threadpool(
        client.search,
        collection_name=config.COLLECTION_NAME,
        query_vector=query_vector.tolist(),
        query_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(value=user_id)
                ),
                models.FieldCondition(
                    key="document_id",
                    match=models.MatchValue(value=document_id)
                )
            ]
        ),
        limit=10 
    )

    rerank_pairs = []
    for result in search_results:
        rerank_pairs.append([query, result.payload["text"]])

    if not rerank_pairs:
        return []

    print(f"Reranking {len(rerank_pairs)} chunks...")
    scores = await run_in_threadpool(rerank_model.predict, rerank_pairs)
    print("Reranking complete.")

    results_with_scores = list(zip(search_results, scores))
    results_with_scores.sort(key=lambda x: x[1], reverse=True)

    context = []
    for result, score in results_with_scores[:3]: 
        context.append({
            "text": result.payload["text"],
            "source_file": result.payload["file_name"],
            "page": result.payload.get("page_number", 0),
            "original_score": float(result.score), 
            "rerank_score": float(score) 
        })
        
    return context

async def run_conversational_rag(
    user_id: str,
    document_id: str,
    query: str,
    chat_history: List[BaseMessage]
) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Runs the full conversational RAG chain:
    1. Rephrases query based on history.
    2. Retrieves context using the rephrased query.
    3. Generates an answer based on history, context, and original query.
    """

    # --- Step 1: Rephrase the query ---
    rephrasing_prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{query}"),
        ("user", "Given the above conversation, generate a search query that is a standalone question to look up information. Do not answer the question, just reformulate it.")
    ])
    
    rephrasing_chain = rephrasing_prompt | llm | StrOutputParser()

    if chat_history:
        print("Rephrasing query based on history...")
        standalone_query = await rephrasing_chain.ainvoke({
            "chat_history": chat_history,
            "query": query
        })
        print(f"Original query: {query}")
        print(f"Rephrased query: {standalone_query}")
    else:
        print("No chat history, using original query.")
        standalone_query = query

    context_list = await search_documents(
        user_id=user_id,
        document_id=document_id,
        query=standalone_query
    )
    
    if not context_list:
        return "I could not find any relevant information in the specified document to answer your question.", []

    answer_prompt = ChatPromptTemplate.from_messages([
        ("system", "Answer the user's question based ONLY on the context below. If the context doesn't contain the answer, say so.\n\nContext:\n{context}"),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{query}"),
    ])
    
    answer_chain = answer_prompt | llm | StrOutputParser()
    
    combined_context = "\n\n---\n\n".join([chunk["text"] for chunk in context_list])
    
    print("Generating final answer...")
    answer = await answer_chain.ainvoke({
        "context": combined_context,
        "chat_history": chat_history,
        "query": query 
    })

    return answer, context_list

async def get_documents_by_user(user_id: str) -> List[Dict[str, str]]:
    """
    Retrieves a unique list of all documents uploaded by a specific user
    by scrolling through all their associated points.
    """
    print(f"Fetching document list for user_id: {user_id}")
    
    # This set will store unique (document_id, file_name) tuples
    unique_documents = set()
    next_page_offset = None
    
    while True:
        # Run the blocking scroll call in a thread pool
        scroll_results = await run_in_threadpool(
            client.scroll,
            collection_name=config.COLLECTION_NAME,
            scroll_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="user_id",
                        match=models.MatchValue(value=user_id)
                    )
                ]
            ),
            limit=200,  # Process 200 chunks at a time
            offset=next_page_offset,
            with_payload=True,  # We only need the payload
            with_vectors=False # No need for vectors, saves bandwidth
        )
        
        points = scroll_results[0]
        next_page_offset = scroll_results[1]
        
        for point in points:
            payload = point.payload
            doc_id = payload.get("document_id")
            file_name = payload.get("file_name")
            
            # Add the doc info to the set (duplicates are automatically ignored)
            if doc_id and file_name:
                unique_documents.add((doc_id, file_name))
        
        # If next_page_offset is None, we've processed all points
        if not next_page_offset:
            break
            
    print(f"Found {len(unique_documents)} unique documents for user {user_id}.")
    
    # Format the set of tuples into a list of dictionaries for the response
    document_list = [
        {"document_id": doc_id, "file_name": file_name}
        for doc_id, file_name in unique_documents
    ]
    
    return document_list
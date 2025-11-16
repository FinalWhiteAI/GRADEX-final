# api.py
import os
import uuid
import aiofiles
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Request
from typing import Dict, List  # <-- ADDED
import httpx
from pydantic import BaseModel

# Import schemas and service functions
import schemas
import service as services

# --- ADDED: Imports for Chat History ---
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

router = APIRouter()

# --- ADDED: In-Memory Chat History Database ---
# (Replace this with Redis or another DB for production)
CHAT_HISTORY_DB: Dict[str, List[BaseMessage]] = {}


@router.get("/documents/{user_id}", response_model=schemas.DocumentListResponse)
async def get_user_documents(user_id: str):
    """
    Retrieves a list of all documents associated with a specific user_id.
    """
    try:
        documents = await services.get_documents_by_user(user_id)
        return schemas.DocumentListResponse(documents=documents)
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching documents for user {user_id}: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while fetching documents: {str(e)}"
        )

@router.post("/upload/", response_model=schemas.UploadResponse)
async def upload_file(
    user_id: str = Form(...),
    file: UploadFile = File(...)):
    # (This endpoint remains unchanged)
    temp_file_path = f"temp_{uuid.uuid4()}_{file.filename}"
    try:
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)
        chunks = services.load_and_split_document(temp_file_path, file.filename)
        chunks_stored, document_id = await services.embed_and_store_chunks(
            chunks, user_id, file.filename
        )
        return schemas.UploadResponse(
            message=f"Successfully embedded and stored {chunks_stored} chunks.",
            chunks_stored=chunks_stored,
            file_name=file.filename,
            user_id=user_id,
            document_id=document_id
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# @router.post("/query/", response_model=schemas.QueryResponse)
# async def query_documents(request: schemas.QueryRequest):
#     # (This endpoint remains unchanged)
#     try:
#         context = await services.search_documents(
#             user_id=request.user_id,
#             document_id=request.document_id,
#             query=request.query
#         )
#         return schemas.QueryResponse(context=context)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error during query: {str(e)}")


# --- UPDATED: /query/rag/ endpoint ---
@router.post("/query/rag/", response_model=schemas.RAGQueryResponse)
async def query_rag(request: schemas.RAGQueryRequest): # <-- Use new schema
    """
    Performs Conversational RAG:
    1. Fetches chat history.
    2. Rephrases the query based on history.
    3. Retrieves context (with reranking).
    4. Passes history, context, and query to an LLM.
    5. Returns the final answer and saves history.
    """
    try:
        # 1. Fetch history from our "DB"
        chat_history = CHAT_HISTORY_DB.get(request.chat_session_id, [])

        # 2. Call the new conversational RAG service function
        #    This function will handle all the complex logic.
        answer, context_list = await services.run_conversational_rag(
            user_id=request.user_id,
            document_id=request.document_id,
            query=request.query,
            chat_history=chat_history
        )
        
        # 3. Update the history in our "DB"
        chat_history.append(HumanMessage(content=request.query))
        chat_history.append(AIMessage(content=answer))
        CHAT_HISTORY_DB[request.chat_session_id] = chat_history

        return schemas.RAGQueryResponse(answer=answer, context=context_list)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during RAG query: {str(e)}")
    
class UrlUploadPayload(BaseModel):
    user_id: str
    file_url:str
async def _process_and_store_file(
    temp_file_path: str, 
    user_id: str, 
    file_name: str
):
    """
    Internal helper to process a file that is already on disk.
    """
    try:
        chunks = services.load_and_split_document(temp_file_path, file_name)
        chunks_stored, document_id = await services.embed_and_store_chunks(
            chunks, user_id, file_name
        )
        return schemas.UploadResponse(
            message=f"Successfully embedded and stored {chunks_stored} chunks.",
            chunks_stored=chunks_stored,
            file_name=file_name,
            user_id=user_id,
            document_id=document_id
        )
    except Exception as e:
        # Re-raise to be caught by the endpoint's handler
        raise HTTPException(
            status_code=500, 
            detail=f"Error during service processing: {str(e)}"
        )

@router.post("/upload-from-url/", response_model=schemas.UploadResponse)
async def upload_from_url(payload: UrlUploadPayload):
    """
    Fetches a PDF from a pre-defined URL based on user_id, 
    saves it, and processes it.
    """
    user_id = payload.user_id
    file_url=payload.file_url
    print(payload)
    
    # 1. Construct the URL and a filename
    fetch_url = f"{file_url}"
    file_name = f"{user_id}_notes.pdf"
    temp_file_path = f"temp_{uuid.uuid4()}_{file_name}"

    try:
        # 2. Fetch the PDF from the URL
        async with httpx.AsyncClient() as client:
            response = await client.get(fetch_url)
            response.raise_for_status() # Raise an error for 4xx/5xx responses
            print(response)
            # Good practice: check if it's actually a PDF
            if "application/pdf" not in response.headers.get("content-type", ""):
                raise HTTPException(status_code=400, detail="Fetched content is not a PDF.")
            
            # 3. Save the fetched content to disk
            async with aiofiles.open(temp_file_path, 'wb') as out_file:
                await out_file.write(response.content)

        # 4. Call the *same* shared helper
        return await _process_and_store_file(temp_file_path, user_id, file_name)

    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"Failed to fetch notes: {exc}")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Error during PDF fetch: {str(exc)}")
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
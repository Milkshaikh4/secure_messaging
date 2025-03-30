from fastapi import FastAPI, HTTPException, Depends, status
from typing import List

from app.database import messages_collection
from app.auth import get_current_user, create_jwt_token
from app.schemas import MessageCreate, MessageOut
from app.encryption import encrypt_message, decrypt_message

app = FastAPI()

@app.get("/login/{user_id}")
def fake_login(user_id: str):
    """
    Trivial endpoint to generate a JWT for testing.
    """
    token = create_jwt_token(user_id)
    return {"token": token}

@app.post("/messages", response_model=dict)
async def create_message(
    payload: MessageCreate,
    user_id: str = Depends(get_current_user)
):
    """
    Encrypt and store a message for the authenticated user.
    """
    try:
        encrypted_text = encrypt_message(payload.text)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to encrypt message: {exc}"
        )

    doc = {
        "user_id": user_id,
        "encrypted_text": encrypted_text
    }

    try:
        result = await messages_collection.insert_one(doc)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to store message in the database: {exc}"
        )
    
    return {"inserted_id": str(result.inserted_id)}


@app.get("/messages/{request_user_id}", response_model=List[MessageOut])
async def get_messages(
    request_user_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Retrieve all messages for user_id. 
    Only allow if request_user_id == user_id to avoid spoofing.
    """
    if request_user_id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        cursor = messages_collection.find({"user_id": user_id})
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to query messages from database: {exc}"
        )
        
    messages = []
    async for doc in cursor:
        try:
            decrypted_text = decrypt_message(doc["encrypted_text"])
        except Exception as exc:
            raise HTTPException(
                status_code=422, 
                detail=f"Failed to decrypt message with id {str(doc['_id'])}: {exc}"
            )        
        
        messages.append(
            MessageOut(
                id=str(doc["_id"]),
                user_id=doc["user_id"],
                decrypted_text=decrypted_text
            )
        )
    return messages
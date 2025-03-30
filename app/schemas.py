from pydantic import BaseModel

class MessageCreate(BaseModel):
    text: str

class DebugDecrypt(BaseModel):
    encrypted: str

class MessageOut(BaseModel):
    id: str
    user_id: str
    decrypted_text: str

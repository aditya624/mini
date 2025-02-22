import base64
from pydantic import BaseModel, Field

# byte to base64
def bytes_to_base64(image_bytes):
    return base64.b64encode(image_bytes).decode('utf-8')

class GoogleSearchSchema(BaseModel):
    query: str = Field(description="The search query.")
    type: str = Field(description="The search type one of 'images', 'search', 'news' or 'places'. if not provided, it defaults to 'search'")

class MultimodalSchema(BaseModel):
    question: str = Field(description="The question.")

class ArxivSchema(BaseModel):
    query: str = Field(description="The search query.")
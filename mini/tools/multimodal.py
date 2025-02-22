import os
from google import genai
from google.genai.types import HttpOptions
from google.genai import types

class Multimodal:
    def __init__(self):
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def extract(self, question, base64_image):
        if not base64_image:
            return "Please upload an image."

        response = self.client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[
                    question,
                    types.Part.from_bytes(data=base64_image, mime_type="image/jpeg")
                ]
            )
        
        return response.text
import requests
from transformers import AutoProcessor, AutoModel
from typing import List
import ollama
from PIL import Image
import base64


class LLM():
    def __init__(self):
        self.client = ollama.Client()
        self.embedding_model_name = "nomic-embed-text"
        self.ai_model_name = "qwen3"

    def embed_text(self, content: str) -> List[float]:
        result = self.client.embeddings(
            model=self.embedding_model_name,
            prompt=content,
        )

        return result.embedding

    def embed_image(self, file_path: str) -> List[str | List[float]]:
        # Open and convert image to base64
        with open(file_path, 'rb') as image_file:
            image_data = base64.b64encode(image_file.read()).decode('utf-8')

        # Get image description from the model
        response = self.client.chat(
            model="gemma3:4b",
            messages=[
                {
                    'role': 'user',
                    'content': """
                        Describe this image with all distinct features, colors and other important details.
                        Make sure to give description in maximum 50 words and single line containing all important details.
                        Do not add extra commentry at beginning or end.
                      """,
                    'images': [image_data]
                }
            ]
        )

        # Extract the description from response
        image_description = response['message']['content']

        # Convert the description to vector embedding
        return [image_description, self.embed_text(image_description)]

    def chat(self, query, context):
        PROMPT = f"""
          Answer user question based on given context.
          Just answer from context and if there is no information found in context then say i'm sorry i cannot find that information with external_id: -1.

          query:
            {query}
          
          context:
            {context}

          output format:
            external_id: {{relevent external_id}}
            response: {{your response goes here}}
        """

        stream = self.client.chat(
            model=self.ai_model_name,
            messages=[
                {
                    'role': 'user',
                    'content': PROMPT
                }
            ],
            stream=True,
        )

        return stream

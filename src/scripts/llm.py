from typing import List
import ollama


class LLM():
    def __init__(self):
        self.client = ollama.Client()
        self.embedding_model_name = "mxbai-embed-large"
        self.ai_model_name = "qwen3"

    def embed_content(self, content: str) -> List[float]:
        result = self.client.embeddings(
            model=self.embedding_model_name,
            prompt=content
        )

        return result.embedding

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
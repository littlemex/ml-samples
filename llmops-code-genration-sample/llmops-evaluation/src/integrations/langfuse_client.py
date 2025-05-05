from langfuse import Langfuse
import os
from dotenv import load_dotenv

load_dotenv()

class LangfuseClient:
    def __init__(self):
        self.client = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST")
        )

    def create_generation(self, name: str, model: str, prompt: str, completion: str, 
                         start_time: float, end_time: float, tokens: int):
        return self.client.generation(
            name=name,
            model=model,
            prompt=prompt,
            completion=completion,
            start_time=start_time,
            end_time=end_time,
            metadata={
                "tokens": tokens,
            }
        )

    def log_score(self, generation_id: str, name: str, value: float):
        return self.client.score(
            generation_id=generation_id,
            name=name,
            value=value
        )

    def log_metric(self, name: str, value: float, metadata: dict = None):
        return self.client.metric(
            name=name,
            value=value,
            metadata=metadata or {}
        )
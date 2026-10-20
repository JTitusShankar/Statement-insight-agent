import os

from dotenv import load_dotenv
from strands.models.litellm import LiteLLMModel

load_dotenv()

def get_model() -> LiteLLMModel:
    """Return the chat model used by the agent."""
    api_key = os.getenv("GROQ_API_KEY")

    return LiteLLMModel(
        client_args = {"api_key":api_key}, 
        model_id="groq/openai/gpt-oss-20b"
        )
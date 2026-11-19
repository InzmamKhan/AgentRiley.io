import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    NVIDIA_API_KEY: str = "your_nvidia_api_key_here"
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    NVIDIA_LLM_MODEL: str = "meta/llama-3.1-70b-instruct"
    
    # FastEmbed Model (Local high-speed quantized embeddings)
    FASTEMBED_MODEL_NAME: str = "BAAI/bge-small-en-v1.5"

    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000
    
    DOCUMENTS_DIR: str = "./documents"
    
    # Chunking config
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K: int = 4

    class Config:
        env_file = ".env"
        extra = "allow"

settings = Settings()

# Ensure tactical drop folder exists
Path(settings.DOCUMENTS_DIR).mkdir(parents=True, exist_ok=True)

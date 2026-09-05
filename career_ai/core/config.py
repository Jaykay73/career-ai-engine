"""
Configuration module using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    app_env: str = Field(default="development", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # LLM Settings
    llm_provider: str = Field(default="deepseek", alias="LLM_PROVIDER")
    deepseek_api_key: Optional[str] = Field(default=None, alias="DEEPSEEK_API_KEY")
    deepseek_model: str = Field(default="deepseek-chat", alias="DEEPSEEK_MODEL")
    deepseek_base_url: str = Field(default="https://api.deepseek.com", alias="DEEPSEEK_BASE_URL")

    # Embeddings
    embedding_model: str = Field(default="BAAI/bge-small-en-v1.5", alias="EMBEDDING_MODEL")

    # Vector Store (Qdrant)
    qdrant_storage_path: Path = Field(default=Path("./data/qdrant_db"), alias="QDRANT_STORAGE_PATH")
    qdrant_collection: str = Field(default="career_knowledge", alias="QDRANT_COLLECTION")
    qdrant_host: Optional[str] = Field(default=None, alias="QDRANT_HOST")
    qdrant_port: Optional[int] = Field(default=None, alias="QDRANT_PORT")

    # Hybrid Retrieval & RRF
    rrf_k: int = Field(default=60, alias="RRF_K")
    top_k_bm25: int = Field(default=20, alias="TOP_K_BM25")
    top_k_vector: int = Field(default=20, alias="TOP_K_VECTOR")
    top_k_rrf: int = Field(default=12, alias="TOP_K_RRF")

    # Directories
    data_dir: Path = Field(default=Path("./data"), alias="DATA_DIR")
    output_dir: Path = Field(default=Path("./output"), alias="OUTPUT_DIR")
    knowledge_dir: Path = Field(default=Path("./knowledge"), alias="KNOWLEDGE_DIR")
    templates_dir: Path = Field(default=Path("./templates"), alias="TEMPLATES_DIR")

    # SQLite Database
    sqlite_db_name: str = "career_ai.db"

    # LaTeX Settings
    latex_enabled: bool = Field(default=True, alias="LATEX_ENABLED")
    latex_compiler: str = Field(default="pdflatex", alias="LATEX_COMPILER")
    latex_timeout_seconds: int = Field(default=30, alias="LATEX_TIMEOUT_SECONDS")

    @property
    def sqlite_db_path(self) -> Path:
        return self.data_dir / self.sqlite_db_name

    def ensure_directories(self) -> None:
        """Ensures that all runtime data and output directories exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.knowledge_dir.mkdir(parents=True, exist_ok=True)
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        if not self.qdrant_host:
            self.qdrant_storage_path.mkdir(parents=True, exist_ok=True)

# Global singleton
settings = Settings()
settings.ensure_directories()

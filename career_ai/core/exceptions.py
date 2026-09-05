"""
Typed domain exceptions for the Career AI application.
"""

class CareerAIError(Exception):
    """Base exception for all Career AI errors."""
    pass

class ConfigurationError(CareerAIError):
    """Raised when configuration is missing or invalid."""
    pass

class KnowledgeBaseError(CareerAIError):
    """Raised when knowledge base operations fail."""
    pass

class ParsingError(KnowledgeBaseError):
    """Raised when parsing markdown or structured records fails."""
    pass

class RetrievalError(CareerAIError):
    """Raised when retrieval (BM25 or vector search) fails."""
    pass

class EmbeddingError(RetrievalError):
    """Raised when embedding generation fails."""
    pass

class LLMProviderError(CareerAIError):
    """Base exception for LLM provider errors."""
    pass

class LLMAuthenticationError(LLMProviderError):
    """Raised when LLM API key is missing or invalid."""
    pass

class LLMResponseError(LLMProviderError):
    """Raised when LLM returns invalid or unparseable output."""
    pass

class JobAnalysisError(CareerAIError):
    """Raised when job description analysis fails."""
    pass

class VerificationError(CareerAIError):
    """Raised when post-generation verification detects unsupported claims."""
    pass

class LaTeXError(CareerAIError):
    """Base exception for LaTeX operations."""
    pass

class LaTeXCompilationError(LaTeXError):
    """Raised when LaTeX compilation to PDF fails."""
    def __init__(self, message: str, log_output: str = ""):
        super().__init__(message)
        self.log_output = log_output

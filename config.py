"""
Configuration and logging setup for HR Policy Assistant
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional


# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration management for HR Policy Assistant"""
    
    # API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "llama-3.3-70b-versatile")
    
    # Model Configuration
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    
    # RAG Configuration
    CHROMADB_COLLECTION_NAME: str = "hr_policies"
    RAG_TOP_K: int = 3
    
    # Agent Configuration
    TEMPERATURE: float = 0.3
    MAX_EVAL_RETRIES: int = 2
    FAITHFULNESS_THRESHOLD: float = 0.7
    
    # Memory Configuration
    MEMORY_WINDOW_SIZE: int = 6  # Last N messages
    
    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_SERVER_PORT", 8501))
    STREAMLIT_HEADLESS: bool = os.getenv("STREAMLIT_SERVER_HEADLESS", "false").lower() == "true"
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = "hr_policy_assistant.log"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration"""
        if not cls.GROQ_API_KEY:
            logging.warning("GROQ_API_KEY not set. Please set it in .env file or environment variables.")
            return False
        return True
    
    @classmethod
    def get_summary(cls) -> str:
        """Get configuration summary"""
        return f"""
Configuration Summary:
- LLM Model: {cls.LLM_MODEL}
- Embedding Model: {cls.EMBEDDING_MODEL}
- Temperature: {cls.TEMPERATURE}
- RAG Top K: {cls.RAG_TOP_K}
- Faithfulness Threshold: {cls.FAITHFULNESS_THRESHOLD}
- Memory Window Size: {cls.MEMORY_WINDOW_SIZE}
- Max Eval Retries: {cls.MAX_EVAL_RETRIES}
- Log Level: {cls.LOG_LEVEL}
"""


def setup_logging(log_level: Optional[str] = None) -> logging.Logger:
    """
    Setup logging configuration for the application.
    
    Args:
        log_level: Override log level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        logging.Logger: Configured logger
    """
    level = log_level or Config.LOG_LEVEL
    
    # Create logger
    logger = logging.getLogger("hr_policy_assistant")
    logger.setLevel(getattr(logging, level))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, level))
    
    # File handler
    file_handler = logging.FileHandler(Config.LOG_FILE)
    file_handler.setLevel(getattr(logging, level))
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add handlers
    if not logger.handlers:
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger


# Initialize logger
logger = setup_logging()


def log_agent_interaction(question: str, route: str, faithfulness: float, sources: int):
    """Log agent interaction for analytics"""
    logger.info(
        f"Agent Interaction - Question: {question[:50]}... | "
        f"Route: {route} | Faithfulness: {faithfulness:.2f} | Sources: {sources}"
    )


def log_error(error_type: str, error_message: str):
    """Log error with context"""
    logger.error(f"{error_type}: {error_message}")


def log_debug(message: str):
    """Log debug information"""
    logger.debug(message)

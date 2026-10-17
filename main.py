"""
Main entry point for the Smart Kitchen Queue Management System.
"""

import uvicorn
import logging
from app.config import config

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main application entry point."""
    logger.info("Starting Smart Kitchen Queue Management System")
    
    # Validate configuration
    if not config.validate():
        logger.error("Configuration validation failed")
        return
    
    logger.info(f"Configuration validated successfully")
    logger.info(f"Excel file path: {config.EXCEL_FILE_PATH}")
    logger.info(f"Ollama URL: {config.OLLAMA_BASE_URL}")
    logger.info(f"API will run on {config.API_HOST}:{config.API_PORT}")
    
    # Start the FastAPI application
    uvicorn.run(
        "app.main:app",
        host=config.API_HOST,
        port=config.API_PORT,
        reload=config.DEBUG_MODE,
        log_level=config.LOG_LEVEL.lower()
    )


if __name__ == "__main__":
    main()

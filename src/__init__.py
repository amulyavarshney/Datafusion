"""
DataFusion
---------
Advanced File Merger Application

DataFusion is a Streamlit application for merging multiple files with advanced
options and data transformations.
"""

import logging
import os
import sys

# Configure logging
def configure_logging():
    """Configure the logging system for the application."""
    # Create logs directory if it doesn't exist
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Log file path
    log_file = os.path.join(logs_dir, 'datafusion.log')
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set third-party loggers to WARNING level to reduce noise
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('pandas').setLevel(logging.WARNING)
    logging.getLogger('streamlit').setLevel(logging.WARNING)
    
    # Create a logger for this module
    logger = logging.getLogger(__name__)
    logger.info("Logging configured")
    
    return logger

# Initialize the application
def initialize_app():
    """Initialize the application and all its components."""
    logger = configure_logging()
    
    logger.info("Initializing DataFusion application")
    
    # Initialize plugins
    from src.plugins import initialize_plugins
    initialize_plugins()
    
    # Import controllers to register them
    import src.controllers
    
    logger.info("Application initialization complete")

# Call initialize_app when this module is imported
initialize_app()

# Version information
__version__ = '1.0.0'
__author__ = 'Amulya Varshney'
__license__ = 'MIT'
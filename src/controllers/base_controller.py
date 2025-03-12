"""
Base Controller
--------------
Abstract base class for all controllers in the application.
"""

from abc import ABC, abstractmethod
import logging

class BaseController(ABC):
    """
    Abstract base class that all controllers should inherit from.
    
    Provides common functionality and enforces a consistent interface
    across different controllers.
    """
    
    def __init__(self):
        """
        Initialize the base controller.
        
        Sets up logging and any other common initialization.
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def handle(self):
        """
        Main handler method that each controller must implement.
        
        This method is responsible for orchestrating the entire workflow
        for the controller, including rendering UI, processing data, and
        handling user interactions.
        """
        pass
        
    def log_info(self, message):
        """Log an info message."""
        self.logger.info(message)
        
    def log_error(self, message, exc_info=False):
        """Log an error message, optionally with exception info."""
        self.logger.error(message, exc_info=exc_info)
        
    def log_warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
        
    def log_debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
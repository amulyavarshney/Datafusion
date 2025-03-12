"""
Controllers Package
-----------------
Controllers handle the business logic of the DataFusion application.
"""

import importlib
import logging
import inspect
import os
import pkgutil

from src.controllers.base_controller import BaseController

logger = logging.getLogger(__name__)

# Dictionary to store registered controllers by name
_controllers = {}

def register_controller(cls):
    """
    Decorator to register a controller class.
    
    Args:
        cls: The controller class to register
        
    Returns:
        The original class
    """
    if not issubclass(cls, BaseController):
        raise TypeError("Controller must inherit from BaseController")
        
    # Use the class name as the key
    controller_name = cls.__name__
    _controllers[controller_name] = cls
    
    return cls

def get_controller(name):
    """
    Get a controller class by name.
    
    Args:
        name: The name of the controller class
        
    Returns:
        The controller class or None if not found
    """
    return _controllers.get(name)

def get_all_controllers():
    """
    Get all registered controllers.
    
    Returns:
        Dictionary of controller classes by name
    """
    return _controllers.copy()

def initialize_controllers():
    """
    Discover and register all controller classes in this package.
    """
    # Get the directory of this package
    package_dir = os.path.dirname(__file__)
    
    # Auto-register all controller classes
    for _, module_name, is_pkg in pkgutil.iter_modules([package_dir]):
        # Skip __init__ and base_controller modules
        if module_name in ['__init__', 'base_controller']:
            continue
            
        try:
            # Import the module
            module = importlib.import_module(f"src.controllers.{module_name}")
            
            # Find all controller classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, BaseController) and 
                    obj is not BaseController):
                    # Register the controller
                    register_controller(obj)
                    logger.info(f"Registered controller: {name}")
                    
        except Exception as e:
            logger.error(f"Error loading controller module {module_name}: {str(e)}", exc_info=True)

# Initialize controllers when this module is imported
initialize_controllers()

# Import and register FileMerger explicitly to ensure it's available
from src.controllers.file_merger import FileMerger
register_controller(FileMerger)
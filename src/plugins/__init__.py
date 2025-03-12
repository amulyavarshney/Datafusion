"""
Plugins System
------------
Provides extensibility for the DataFusion application.
"""

import logging
import os

logger = logging.getLogger(__name__)

def get_plugin_info():
    """
    Get information about available plugins.
    
    Returns:
        Dictionary with plugin categories and counts
    """
    plugin_info = {}
    
    # Get the directory of this package
    package_dir = os.path.dirname(__file__)
    
    # Iterate through subdirectories (plugin categories)
    for item in os.listdir(package_dir):
        category_path = os.path.join(package_dir, item)
        
        # Skip non-directories and __pycache__
        if not os.path.isdir(category_path) or item == '__pycache__':
            continue
            
        # Count Python files in the directory (excluding __init__.py)
        python_files = [f for f in os.listdir(category_path)
                       if f.endswith('.py') and f != '__init__.py']
        
        # Add to plugin info
        plugin_info[item] = len(python_files)
        
    return plugin_info

def initialize_plugins():
    """Initialize all plugin modules."""
    try:
        # Import data transformers to register them
        from src.plugins import data_transformers
        
        # Log the number of loaded transformers
        num_transformers = len(data_transformers.get_all_transformers())
        logger.info(f"Loaded {num_transformers} data transformers")
        
        # Add other plugin types here as they are developed
        
    except Exception as e:
        logger.error(f"Error initializing plugins: {str(e)}", exc_info=True)
"""
Data Transformers Plugin System
------------------------------
Provides extensible data transformation capabilities for DataFusion.
"""

from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, Any, List, Optional, Union
import importlib
import os
import pkgutil
import inspect
import logging

logger = logging.getLogger(__name__)

class DataTransformer(ABC):
    """
    Abstract base class for all data transformers.
    
    Data transformers are plugins that provide additional data transformation
    capabilities to DataFusion beyond the built-in transformations.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the transformer (displayed in the UI)."""
        pass
        
    @property
    @abstractmethod
    def description(self) -> str:
        """A short description of what the transformer does."""
        pass
        
    @abstractmethod
    def get_parameters(self) -> List[Dict[str, Any]]:
        """
        Get the parameters required by this transformer.
        
        Returns:
            A list of parameter dictionaries, each containing:
                - name: Parameter name
                - type: Parameter type (string, number, boolean, select)
                - label: Display label
                - default: Default value
                - required: Whether the parameter is required
                - options: For 'select' type, a list of options
        """
        pass
        
    @abstractmethod
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """
        Apply the transformation to the dataframe.
        
        Args:
            df: Input DataFrame
            params: Dictionary of parameters for the transformation
            
        Returns:
            Transformed DataFrame
        """
        pass
        
    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, str]:
        """
        Validate the provided parameters against the required parameters.
        
        Args:
            params: Dictionary of parameters to validate
            
        Returns:
            Dictionary of error messages keyed by parameter name, or empty dict if valid
        """
        errors = {}
        required_params = [p for p in self.get_parameters() if p.get('required', False)]
        
        for param in required_params:
            name = param['name']
            if name not in params or params[name] is None or params[name] == '':
                errors[name] = f"Parameter '{param['label']}' is required"
                
        return errors


# Dictionary to store registered transformers
_transformers = {}

def register_transformer(cls):
    """
    Decorator to register a data transformer.
    
    Args:
        cls: The DataTransformer class to register
        
    Returns:
        The original class
    """
    if not issubclass(cls, DataTransformer):
        raise TypeError("Class must inherit from DataTransformer")
        
    instance = cls()
    _transformers[instance.name] = instance
    return cls

def get_transformer(name: str) -> Optional[DataTransformer]:
    """
    Get a registered transformer by name.
    
    Args:
        name: The name of the transformer
        
    Returns:
        The transformer instance, or None if not found
    """
    return _transformers.get(name)

def get_all_transformers() -> Dict[str, DataTransformer]:
    """
    Get all registered transformers.
    
    Returns:
        Dictionary of transformer instances keyed by name
    """
    return _transformers.copy()

def apply_transformer(
    df: pd.DataFrame, 
    transformer_name: str, 
    params: Dict[str, Any]
) -> Union[pd.DataFrame, Dict[str, str]]:
    """
    Apply a named transformer to a dataframe.
    
    Args:
        df: Input DataFrame
        transformer_name: Name of the transformer to apply
        params: Parameters for the transformation
        
    Returns:
        Either the transformed DataFrame or a dictionary of error messages
    """
    transformer = get_transformer(transformer_name)
    
    if transformer is None:
        return {"error": f"Transformer '{transformer_name}' not found"}
        
    # Validate parameters
    errors = transformer.validate_parameters(params)
    if errors:
        return errors
        
    try:
        # Apply the transformation
        return transformer.transform(df, params)
    except Exception as e:
        logger.error(f"Error applying transformer '{transformer_name}': {str(e)}", exc_info=True)
        return {"error": f"Error applying transformer: {str(e)}"}

# Automatically discover and load all transformers in this package
def discover_transformers():
    """Discover and load all transformer modules in this package."""
    # Get the directory of this module
    package_dir = os.path.dirname(__file__)
    
    # Iterate through all modules in this package
    for _, module_name, _ in pkgutil.iter_modules([package_dir]):
        # Skip __init__ module
        if module_name == '__init__':
            continue
            
        try:
            # Import the module
            module = importlib.import_module(f"{__name__}.{module_name}")
            
            # Find all DataTransformer subclasses in the module
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, DataTransformer) and 
                    obj is not DataTransformer):
                    # Register the transformer
                    register_transformer(obj)
                    logger.info(f"Registered transformer: {obj().name}")
        except Exception as e:
            logger.error(f"Error loading transformer module {module_name}: {str(e)}", exc_info=True)

# Discover transformers when this module is imported
discover_transformers()
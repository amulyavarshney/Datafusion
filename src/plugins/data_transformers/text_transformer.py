"""
Text Transformers
----------------
Plugin with various text transformation operations.
"""

import pandas as pd
import re
from typing import Dict, Any, List

from src.plugins.data_transformers import DataTransformer, register_transformer

@register_transformer
class TextCaseTransformer(DataTransformer):
    """
    Transformer to change the case of text data in a column.
    """
    
    @property
    def name(self) -> str:
        return "Text Case Transformer"
        
    @property
    def description(self) -> str:
        return "Change the case of text data in a column (uppercase, lowercase, title case)"
        
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'column',
                'type': 'select',
                'label': 'Column',
                'required': True,
                'dynamic_options': True  # This will be populated with column names
            },
            {
                'name': 'case_type',
                'type': 'select',
                'label': 'Case Type',
                'required': True,
                'default': 'lower',
                'options': [
                    {'value': 'lower', 'label': 'Lowercase'},
                    {'value': 'upper', 'label': 'Uppercase'},
                    {'value': 'title', 'label': 'Title Case'},
                    {'value': 'sentence', 'label': 'Sentence case'}
                ]
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Change the case of text in a column."""
        result = df.copy()
        
        column = params.get('column')
        case_type = params.get('case_type', 'lower')
        
        if column not in result.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
            
        # Convert to string type if needed
        result[column] = result[column].astype(str)
        
        if case_type == 'lower':
            result[column] = result[column].str.lower()
        elif case_type == 'upper':
            result[column] = result[column].str.upper()
        elif case_type == 'title':
            result[column] = result[column].str.title()
        elif case_type == 'sentence':
            # First lowercase everything
            result[column] = result[column].str.lower()
            # Then capitalize the first letter
            result[column] = result[column].str.capitalize()
            
        return result


@register_transformer
class TextPatternExtractor(DataTransformer):
    """
    Transformer to extract text patterns using regular expressions.
    """
    
    @property
    def name(self) -> str:
        return "Text Pattern Extractor"
        
    @property
    def description(self) -> str:
        return "Extract text that matches a pattern and save to a new column"
        
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'source_column',
                'type': 'select',
                'label': 'Source Column',
                'required': True,
                'dynamic_options': True
            },
            {
                'name': 'target_column',
                'type': 'string',
                'label': 'Target Column Name',
                'required': True
            },
            {
                'name': 'pattern',
                'type': 'string',
                'label': 'Regular Expression Pattern',
                'required': True,
                'default': '(\\d+)'
            },
            {
                'name': 'replace_na',
                'type': 'string',
                'label': 'Replacement for Non-Matches',
                'required': False,
                'default': ''
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Extract patterns from text using regex."""
        result = df.copy()
        
        source_column = params.get('source_column')
        target_column = params.get('target_column')
        pattern = params.get('pattern')
        replace_na = params.get('replace_na', '')
        
        if source_column not in result.columns:
            raise ValueError(f"Column '{source_column}' not found in dataframe")
            
        if not pattern:
            raise ValueError("Regular expression pattern cannot be empty")
            
        # Convert to string type if needed
        result[source_column] = result[source_column].astype(str)
        
        try:
            # Extract the pattern
            compiled_pattern = re.compile(pattern)
            
            # Define extraction function
            def extract_pattern(text):
                match = compiled_pattern.search(text)
                if match:
                    return match.group(0)  # Return the entire match
                return replace_na
                
            # Apply the function
            result[target_column] = result[source_column].apply(extract_pattern)
            
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {str(e)}")
            
        return result


@register_transformer
class TextReplaceTransformer(DataTransformer):
    """
    Transformer to replace text patterns in a column.
    """
    
    @property
    def name(self) -> str:
        return "Text Replace Transformer"
        
    @property
    def description(self) -> str:
        return "Replace text patterns in a column using regular expressions"
        
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'column',
                'type': 'select',
                'label': 'Column',
                'required': True,
                'dynamic_options': True
            },
            {
                'name': 'pattern',
                'type': 'string',
                'label': 'Search Pattern (regular expression)',
                'required': True
            },
            {
                'name': 'replacement',
                'type': 'string',
                'label': 'Replacement Text',
                'required': True,
                'default': ''
            },
            {
                'name': 'case_sensitive',
                'type': 'boolean',
                'label': 'Case Sensitive',
                'required': False,
                'default': True
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Replace text patterns in a column."""
        result = df.copy()
        
        column = params.get('column')
        pattern = params.get('pattern')
        replacement = params.get('replacement', '')
        case_sensitive = params.get('case_sensitive', True)
        
        if column not in result.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
            
        if pattern is None or pattern == '':
            raise ValueError("Search pattern cannot be empty")
            
        # Convert to string type if needed
        result[column] = result[column].astype(str)
        
        try:
            # Create flags for regular expression
            flags = 0 if case_sensitive else re.IGNORECASE
            
            # Replace the pattern
            result[column] = result[column].str.replace(
                pattern, replacement, regex=True, flags=flags
            )
            
        except re.error as e:
            raise ValueError(f"Invalid regular expression: {str(e)}")
            
        return result
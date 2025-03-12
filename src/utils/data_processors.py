"""
Data Processors
--------------
Utility functions for processing and transforming data.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import re
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)

def clean_dataframe(df: pd.DataFrame, options: Dict[str, Any] = None) -> pd.DataFrame:
    """
    Clean a DataFrame with various options.
    
    Args:
        df: Input DataFrame
        options: Dictionary with cleaning options:
            - fill_method: Method to fill missing values
            - fill_value: Custom value for filling
            - drop_duplicates: Whether to drop duplicate rows
            - ignore_case: Whether to ignore case in column names
            
    Returns:
        Cleaned DataFrame
    """
    if options is None:
        options = {}
        
    # Make a copy to avoid modifying the original
    result = df.copy()
    
    # Handle column names case
    if options.get('ignore_case', True):
        result.columns = [str(col).lower() for col in result.columns]
        
    # Fill missing values
    if options.get('fill_method') and options.get('fill_method') != "None (keep NaN)":
        if options['fill_method'] == "Zero":
            result = result.fillna(0)
        elif options['fill_method'] == "Mean":
            for col in result.select_dtypes(include=[np.number]).columns:
                result[col] = result[col].fillna(result[col].mean())
        elif options['fill_method'] == "Median":
            for col in result.select_dtypes(include=[np.number]).columns:
                result[col] = result[col].fillna(result[col].median())
        elif options['fill_method'] == "Mode":
            for col in result.columns:
                mode_val = result[col].mode()
                result[col] = result[col].fillna(mode_val[0] if not mode_val.empty else np.nan)
        elif options['fill_method'] == "Forward fill":
            result = result.fillna(method='ffill')
        elif options['fill_method'] == "Backward fill":
            result = result.fillna(method='bfill')
        elif options['fill_method'] == "Custom value" and 'fill_value' in options:
            try:
                # Try to convert to numeric if possible
                fill_val = float(options['fill_value']) if options['fill_value'].replace('.', '', 1).isdigit() else options['fill_value']
                result = result.fillna(fill_val)
            except:
                result = result.fillna(options['fill_value'])
                
    # Handle duplicates
    if options.get('handle_duplicates', False):
        # If join key is specified, drop duplicates based on that column
        if options.get('join_key') and options['join_key'] in result.columns:
            result = result.drop_duplicates(subset=[options['join_key']])
        else:
            result = result.drop_duplicates()
            
    return result

def detect_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Detect duplicates in a DataFrame.
    
    Args:
        df: Input DataFrame
        subset: Columns to consider for identifying duplicates
        
    Returns:
        Dictionary with duplicate information:
            - duplicate_count: Number of duplicate rows
            - duplicate_rows: DataFrame with duplicate rows
            - duplicate_indices: Indices of duplicate rows
    """
    if subset is None:
        # If no subset specified, use all columns
        duplicated = df.duplicated(keep='first')
    else:
        # Check if all subset columns exist in df
        valid_cols = [col for col in subset if col in df.columns]
        if not valid_cols:
            return {
                'duplicate_count': 0,
                'duplicate_rows': pd.DataFrame(),
                'duplicate_indices': []
            }
            
        duplicated = df.duplicated(subset=valid_cols, keep='first')
        
    duplicate_indices = duplicated[duplicated].index.tolist()
    duplicate_rows = df.loc[duplicate_indices]
    
    return {
        'duplicate_count': len(duplicate_indices),
        'duplicate_rows': duplicate_rows,
        'duplicate_indices': duplicate_indices
    }

def suggest_column_mapping(
    source: Union[str, List[str]], 
    target_columns: List[str], 
    threshold: float = 0.8
) -> Union[List[str], Dict[str, str]]:
    """
    Suggest column mappings based on string similarity.
    
    Args:
        source: Source column name or list of column names
        target_columns: List of target column names
        threshold: Similarity threshold (0-1)
        
    Returns:
        If source is a string: List of suggested column names
        If source is a list: Dictionary mapping source columns to target columns
    """
    # Handle single column case
    if isinstance(source, str):
        matches = []
        for target in target_columns:
            similarity = SequenceMatcher(None, source.lower(), target.lower()).ratio()
            if similarity >= threshold:
                matches.append(target)
                
        return sorted(matches, key=lambda x: SequenceMatcher(None, source.lower(), x.lower()).ratio(), reverse=True)
        
    # Handle multiple columns case
    elif isinstance(source, list):
        mapping = {}
        
        for src_col in source:
            best_match = None
            best_score = 0
            
            for tgt_col in target_columns:
                similarity = SequenceMatcher(None, src_col.lower(), tgt_col.lower()).ratio()
                if similarity > best_score and similarity >= threshold:
                    best_score = similarity
                    best_match = tgt_col
                    
            # Only add to mapping if a good match was found
            if best_match:
                mapping[src_col] = best_match
                
        return mapping
        
    return {} if isinstance(source, list) else []

def create_calculated_column(df: pd.DataFrame, column_name: str, expression: str) -> pd.DataFrame:
    """
    Create a new calculated column based on an expression.
    
    Args:
        df: Input DataFrame
        column_name: Name of the new column
        expression: Python expression using column names as variables
        
    Returns:
        DataFrame with the new column added
    """
    result = df.copy()
    
    try:
        # Create a safe local namespace with only the necessary variables
        local_dict = {col: result[col] for col in result.columns if col in expression}
        
        # Add numpy for common math functions
        local_dict['np'] = np
        
        # Evaluate the expression
        result[column_name] = eval(expression, {"__builtins__": {}}, local_dict)
        
        return result
    except Exception as e:
        logger.error(f"Error creating calculated column: {str(e)}", exc_info=True)
        raise ValueError(f"Error creating calculated column: {str(e)}")

def apply_data_transformations(df: pd.DataFrame, transformations: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Apply a series of transformations to a DataFrame.
    
    Args:
        df: Input DataFrame
        transformations: List of transformation dictionaries, each containing:
            - type: Transformation type
            - params: Parameters for the transformation
            
    Returns:
        Transformed DataFrame
    """
    result = df.copy()
    
    for transform in transformations:
        transform_type = transform.get('type')
        params = transform.get('params', {})
        
        try:
            if transform_type == 'create_calculated_column':
                result = create_calculated_column(
                    result,
                    params.get('column_name', 'calculated_column'),
                    params.get('expression', '0')
                )
                
            elif transform_type == 'convert_column_type':
                col_name = params.get('column')
                target_type = params.get('type')
                
                if col_name and col_name in result.columns and target_type:
                    if target_type == 'string':
                        result[col_name] = result[col_name].astype(str)
                    elif target_type == 'number':
                        result[col_name] = pd.to_numeric(result[col_name], errors='coerce')
                    elif target_type == 'datetime':
                        result[col_name] = pd.to_datetime(result[col_name], errors='coerce')
                    elif target_type == 'boolean':
                        result[col_name] = result[col_name].astype(bool)
                        
            elif transform_type == 'replace_values':
                col_name = params.get('column')
                find_val = params.get('find')
                replace_val = params.get('replace')
                
                if col_name and col_name in result.columns and find_val is not None:
                    result[col_name] = result[col_name].replace(find_val, replace_val)
                    
            elif transform_type == 'filter_rows':
                col_name = params.get('column')
                filter_type = params.get('filter_type')
                filter_val = params.get('value')
                
                if col_name and col_name in result.columns and filter_type and filter_val is not None:
                    if filter_type == 'equals':
                        result = result[result[col_name] == filter_val]
                    elif filter_type == 'not_equals':
                        result = result[result[col_name] != filter_val]
                    elif filter_type == 'contains':
                        result = result[result[col_name].astype(str).str.contains(str(filter_val), na=False)]
                    elif filter_type == 'greater_than':
                        try:
                            result = result[pd.to_numeric(result[col_name], errors='coerce') > float(filter_val)]
                        except:
                            pass
                    elif filter_type == 'less_than':
                        try:
                            result = result[pd.to_numeric(result[col_name], errors='coerce') < float(filter_val)]
                        except:
                            pass
                            
            elif transform_type == 'rename_columns':
                rename_dict = params.get('mapping', {})
                if rename_dict:
                    result = result.rename(columns=rename_dict)
                    
            elif transform_type == 'drop_columns':
                cols_to_drop = params.get('columns', [])
                if cols_to_drop:
                    result = result.drop(columns=[col for col in cols_to_drop if col in result.columns])
                    
        except Exception as e:
            logger.error(f"Error applying transformation {transform_type}: {str(e)}", exc_info=True)
            # Continue with the next transformation rather than failing
            
    return result
"""
Numeric Transformers
------------------
Plugin with numerical data transformation operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
import math

from src.plugins.data_transformers import DataTransformer, register_transformer

@register_transformer
class NumericScalingTransformer(DataTransformer):
    """
    Transformer to scale numeric data (normalize, standardize, etc.).
    """
    
    @property
    def name(self) -> str:
        return "Numeric Scaling Transformer"
        
    @property
    def description(self) -> str:
        return "Scale numeric data using various methods (min-max, z-score, etc.)"
        
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
                'name': 'method',
                'type': 'select',
                'label': 'Scaling Method',
                'required': True,
                'default': 'min_max',
                'options': [
                    {'value': 'min_max', 'label': 'Min-Max Scaling (0-1)'},
                    {'value': 'z_score', 'label': 'Z-Score Standardization'},
                    {'value': 'max_abs', 'label': 'Max Absolute Scaling (-1 to 1)'},
                    {'value': 'custom_range', 'label': 'Custom Range Scaling'}
                ]
            },
            {
                'name': 'min_value',
                'type': 'number',
                'label': 'Min Value (for Custom Range)',
                'required': False,
                'default': 0
            },
            {
                'name': 'max_value',
                'type': 'number',
                'label': 'Max Value (for Custom Range)',
                'required': False,
                'default': 100
            },
            {
                'name': 'create_new_column',
                'type': 'boolean',
                'label': 'Create New Column',
                'required': False,
                'default': True
            },
            {
                'name': 'new_column_name',
                'type': 'string',
                'label': 'New Column Name',
                'required': False,
                'default': '',
                'help': "Leave blank to auto-generate based on method"
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Scale numeric data using various methods."""
        result = df.copy()
        
        column = params.get('column')
        method = params.get('method', 'min_max')
        min_value = params.get('min_value', 0)
        max_value = params.get('max_value', 100)
        create_new_column = params.get('create_new_column', True)
        new_column_name = params.get('new_column_name', '')
        
        if column not in result.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
            
        # Try to convert to numeric, coercing errors to NaN
        numeric_data = pd.to_numeric(result[column], errors='coerce')
        
        # Check if we have valid numeric data
        if numeric_data.isna().all():
            raise ValueError(f"Column '{column}' does not contain valid numeric data")
            
        # Auto-generate target column name if not provided
        if create_new_column and not new_column_name:
            if method == 'min_max':
                new_column_name = f"{column}_scaled"
            elif method == 'z_score':
                new_column_name = f"{column}_zscore"
            elif method == 'max_abs':
                new_column_name = f"{column}_maxabs"
            elif method == 'custom_range':
                new_column_name = f"{column}_custom"
        
        # Determine target column
        target_column = new_column_name if create_new_column else column
        
        try:
            # Apply the selected scaling method
            if method == 'min_max':
                min_val = numeric_data.min()
                max_val = numeric_data.max()
                if min_val == max_val:
                    scaled_data = pd.Series(0.5, index=numeric_data.index)
                else:
                    scaled_data = (numeric_data - min_val) / (max_val - min_val)
                
            elif method == 'z_score':
                mean = numeric_data.mean()
                std = numeric_data.std()
                if std == 0:
                    scaled_data = pd.Series(0, index=numeric_data.index)
                else:
                    scaled_data = (numeric_data - mean) / std
                
            elif method == 'max_abs':
                max_abs = max(abs(numeric_data.min()), abs(numeric_data.max()))
                if max_abs == 0:
                    scaled_data = pd.Series(0, index=numeric_data.index)
                else:
                    scaled_data = numeric_data / max_abs
                
            elif method == 'custom_range':
                min_val = numeric_data.min()
                max_val = numeric_data.max()
                if min_val == max_val:
                    # If all values are the same, map to middle of range
                    middle = (min_value + max_value) / 2
                    scaled_data = pd.Series(middle, index=numeric_data.index)
                else:
                    # Map to custom range
                    scaled_data = (numeric_data - min_val) / (max_val - min_val) * (max_value - min_value) + min_value
            
            # Assign the scaled data to the target column
            result[target_column] = scaled_data
            
        except Exception as e:
            raise ValueError(f"Error scaling numeric data: {str(e)}")
            
        return result


@register_transformer
class BinningTransformer(DataTransformer):
    """
    Transformer to bin numeric data into categories.
    """
    
    @property
    def name(self) -> str:
        return "Numeric Binning Transformer"
        
    @property
    def description(self) -> str:
        return "Create categories or groups from numeric data by binning values"
        
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
                'name': 'method',
                'type': 'select',
                'label': 'Binning Method',
                'required': True,
                'default': 'equal_width',
                'options': [
                    {'value': 'equal_width', 'label': 'Equal Width Bins'},
                    {'value': 'equal_freq', 'label': 'Equal Frequency Bins (Quantiles)'},
                    {'value': 'custom', 'label': 'Custom Bin Edges'}
                ]
            },
            {
                'name': 'num_bins',
                'type': 'number',
                'label': 'Number of Bins',
                'required': False,
                'default': 5,
                'min': 2,
                'max': 100
            },
            {
                'name': 'custom_bins',
                'type': 'string',
                'label': 'Custom Bin Edges (comma-separated)',
                'required': False,
                'default': '',
                'help': "e.g., '0,18,35,50,65,100' for age groups"
            },
            {
                'name': 'labels',
                'type': 'string',
                'label': 'Bin Labels (comma-separated, optional)',
                'required': False,
                'default': '',
                'help': "e.g., 'Low,Medium,High' for 3 bins"
            },
            {
                'name': 'target_column',
                'type': 'string',
                'label': 'Target Column Name',
                'required': True,
                'default': ''
            },
            {
                'name': 'include_right',
                'type': 'boolean',
                'label': 'Include Right Edge in Bin',
                'required': False,
                'default': True,
                'help': "If checked, bins include the right edge: (a,b]. Otherwise: [a,b)"
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Bin numeric data into categories."""
        result = df.copy()
        
        column = params.get('column')
        method = params.get('method', 'equal_width')
        num_bins = params.get('num_bins', 5)
        custom_bins_str = params.get('custom_bins', '')
        labels_str = params.get('labels', '')
        target_column = params.get('target_column')
        include_right = params.get('include_right', True)
        
        if column not in result.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
            
        if not target_column:
            raise ValueError("Target column name cannot be empty")
            
        # Convert to numeric data
        numeric_data = pd.to_numeric(result[column], errors='coerce')
        
        # Parse labels if provided
        labels = None
        if labels_str:
            labels = [label.strip() for label in labels_str.split(',')]
            
        try:
            if method == 'custom':
                if not custom_bins_str:
                    raise ValueError("Custom bin edges must be provided")
                    
                # Parse custom bins
                try:
                    bin_edges = [float(edge.strip()) for edge in custom_bins_str.split(',')]
                except:
                    raise ValueError("Invalid bin edges format. Use comma-separated numbers.")
                    
                # Check bin edges
                if len(bin_edges) < 2:
                    raise ValueError("At least 2 bin edges are required")
                    
                # Check if labels match bins
                if labels and len(labels) != len(bin_edges) - 1:
                    raise ValueError(f"Number of labels ({len(labels)}) must be one less than bin edges ({len(bin_edges)})")
                    
                # Create bins
                result[target_column] = pd.cut(
                    numeric_data,
                    bins=bin_edges,
                    labels=labels,
                    include_lowest=True,
                    right=include_right
                )
                
            elif method == 'equal_width':
                # Check num_bins
                if num_bins < 2:
                    raise ValueError("Number of bins must be at least 2")
                    
                # Check if labels match bins
                if labels and len(labels) != num_bins:
                    raise ValueError(f"Number of labels ({len(labels)}) must match number of bins ({num_bins})")
                    
                # Create equal width bins
                result[target_column] = pd.cut(
                    numeric_data,
                    bins=num_bins,
                    labels=labels,
                    include_lowest=True,
                    right=include_right
                )
                
            elif method == 'equal_freq':
                # Check num_bins
                if num_bins < 2:
                    raise ValueError("Number of bins must be at least 2")
                    
                # Check if labels match bins
                if labels and len(labels) != num_bins:
                    raise ValueError(f"Number of labels ({len(labels)}) must match number of bins ({num_bins})")
                    
                # Create equal frequency bins (quantiles)
                result[target_column] = pd.qcut(
                    numeric_data,
                    q=num_bins,
                    labels=labels,
                    duplicates='drop'
                )
                
        except Exception as e:
            raise ValueError(f"Error binning data: {str(e)}")
            
        return result


@register_transformer
class MathOperationTransformer(DataTransformer):
    """
    Transformer to perform mathematical operations on one or more columns.
    """
    
    @property
    def name(self) -> str:
        return "Math Operation Transformer"
        
    @property
    def description(self) -> str:
        return "Apply mathematical operations to create a new column"
        
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'operation',
                'type': 'select',
                'label': 'Operation Type',
                'required': True,
                'default': 'basic',
                'options': [
                    {'value': 'basic', 'label': 'Basic Operation (add, subtract, etc.)'},
                    {'value': 'function', 'label': 'Math Function (log, sqrt, etc.)'},
                    {'value': 'aggregate', 'label': 'Aggregate Multiple Columns'}
                ]
            },
            {
                'name': 'column1',
                'type': 'select',
                'label': 'First Column',
                'required': True,
                'dynamic_options': True
            },
            {
                'name': 'operator',
                'type': 'select',
                'label': 'Operator',
                'required': False,
                'default': '+',
                'options': [
                    {'value': '+', 'label': 'Add (+)'},
                    {'value': '-', 'label': 'Subtract (-)'},
                    {'value': '*', 'label': 'Multiply (*)'},
                    {'value': '/', 'label': 'Divide (/)'},
                    {'value': '%', 'label': 'Modulo (%)'},
                    {'value': '**', 'label': 'Power (**)'}
                ]
            },
            {
                'name': 'column2',
                'type': 'select',
                'label': 'Second Column (for basic operation)',
                'required': False,
                'dynamic_options': True
            },
            {
                'name': 'value',
                'type': 'number',
                'label': 'Value (instead of second column)',
                'required': False,
                'default': 0
            },
            {
                'name': 'use_value',
                'type': 'boolean',
                'label': 'Use Value instead of Second Column',
                'required': False,
                'default': False
            },
            {
                'name': 'function',
                'type': 'select',
                'label': 'Math Function',
                'required': False,
                'default': 'log',
                'options': [
                    {'value': 'log', 'label': 'Natural Logarithm (ln)'},
                    {'value': 'log10', 'label': 'Base-10 Logarithm'},
                    {'value': 'sqrt', 'label': 'Square Root'},
                    {'value': 'abs', 'label': 'Absolute Value'},
                    {'value': 'exp', 'label': 'Exponential (e^x)'},
                    {'value': 'sin', 'label': 'Sine'},
                    {'value': 'cos', 'label': 'Cosine'},
                    {'value': 'tan', 'label': 'Tangent'},
                    {'value': 'round', 'label': 'Round'},
                    {'value': 'floor', 'label': 'Floor'},
                    {'value': 'ceil', 'label': 'Ceiling'}
                ]
            },
            {
                'name': 'aggregate_columns',
                'type': 'string',
                'label': 'Columns to Aggregate (comma-separated)',
                'required': False,
                'default': ''
            },
            {
                'name': 'aggregate_function',
                'type': 'select',
                'label': 'Aggregate Function',
                'required': False,
                'default': 'sum',
                'options': [
                    {'value': 'sum', 'label': 'Sum'},
                    {'value': 'mean', 'label': 'Mean (Average)'},
                    {'value': 'min', 'label': 'Minimum'},
                    {'value': 'max', 'label': 'Maximum'},
                    {'value': 'median', 'label': 'Median'},
                    {'value': 'std', 'label': 'Standard Deviation'},
                    {'value': 'var', 'label': 'Variance'},
                    {'value': 'prod', 'label': 'Product'}
                ]
            },
            {
                'name': 'target_column',
                'type': 'string',
                'label': 'Target Column Name',
                'required': True,
                'default': 'result'
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Apply mathematical operations to create a new column."""
        result = df.copy()
        
        operation = params.get('operation', 'basic')
        column1 = params.get('column1')
        operator = params.get('operator', '+')
        column2 = params.get('column2')
        value = params.get('value', 0)
        use_value = params.get('use_value', False)
        function = params.get('function', 'log')
        aggregate_columns_str = params.get('aggregate_columns', '')
        aggregate_function = params.get('aggregate_function', 'sum')
        target_column = params.get('target_column', 'result')
        
        if column1 not in result.columns:
            raise ValueError(f"Column '{column1}' not found in dataframe")
            
        if not target_column:
            raise ValueError("Target column name cannot be empty")
            
        # Convert column1 to numeric
        col1_data = pd.to_numeric(result[column1], errors='coerce')
        
        try:
            if operation == 'basic':
                # Basic arithmetic operation
                if use_value or not column2:
                    # Use the provided value
                    operand2 = value
                else:
                    # Use the second column
                    if column2 not in result.columns:
                        raise ValueError(f"Column '{column2}' not found in dataframe")
                    operand2 = pd.to_numeric(result[column2], errors='coerce')
                
                # Apply the operation
                if operator == '+':
                    result[target_column] = col1_data + operand2
                elif operator == '-':
                    result[target_column] = col1_data - operand2
                elif operator == '*':
                    result[target_column] = col1_data * operand2
                elif operator == '/':
                    # Handle division by zero
                    if isinstance(operand2, pd.Series):
                        # Replace zeros with NaN to avoid division errors
                        div_operand = operand2.replace(0, np.nan)
                        result[target_column] = col1_data / div_operand
                    else:
                        if operand2 == 0:
                            raise ValueError("Cannot divide by zero")
                        result[target_column] = col1_data / operand2
                elif operator == '%':
                    # Handle modulo by zero
                    if isinstance(operand2, pd.Series):
                        # Replace zeros with NaN to avoid modulo errors
                        mod_operand = operand2.replace(0, np.nan)
                        result[target_column] = col1_data % mod_operand
                    else:
                        if operand2 == 0:
                            raise ValueError("Cannot take modulo by zero")
                        result[target_column] = col1_data % operand2
                elif operator == '**':
                    result[target_column] = col1_data ** operand2
                
            elif operation == 'function':
                # Apply math function
                if function == 'log':
                    # Handle log of non-positive numbers
                    result[target_column] = np.log(col1_data.clip(lower=np.finfo(float).eps))
                elif function == 'log10':
                    # Handle log10 of non-positive numbers
                    result[target_column] = np.log10(col1_data.clip(lower=np.finfo(float).eps))
                elif function == 'sqrt':
                    # Handle sqrt of negative numbers
                    result[target_column] = np.sqrt(col1_data.clip(lower=0))
                elif function == 'abs':
                    result[target_column] = np.abs(col1_data)
                elif function == 'exp':
                    result[target_column] = np.exp(col1_data)
                elif function == 'sin':
                    result[target_column] = np.sin(col1_data)
                elif function == 'cos':
                    result[target_column] = np.cos(col1_data)
                elif function == 'tan':
                    result[target_column] = np.tan(col1_data)
                elif function == 'round':
                    result[target_column] = np.round(col1_data)
                elif function == 'floor':
                    result[target_column] = np.floor(col1_data)
                elif function == 'ceil':
                    result[target_column] = np.ceil(col1_data)
                
            elif operation == 'aggregate':
                if not aggregate_columns_str:
                    raise ValueError("Columns to aggregate must be specified")
                    
                # Parse aggregate columns
                agg_columns = [col.strip() for col in aggregate_columns_str.split(',')]
                
                # Add column1 to the list if not already included
                if column1 not in agg_columns:
                    agg_columns = [column1] + agg_columns
                    
                # Validate all columns exist
                missing_columns = [col for col in agg_columns if col not in result.columns]
                if missing_columns:
                    raise ValueError(f"Columns not found: {', '.join(missing_columns)}")
                    
                # Convert all columns to numeric
                numeric_df = result[agg_columns].apply(pd.to_numeric, errors='coerce')
                
                # Apply aggregate function
                if aggregate_function == 'sum':
                    result[target_column] = numeric_df.sum(axis=1)
                elif aggregate_function == 'mean':
                    result[target_column] = numeric_df.mean(axis=1)
                elif aggregate_function == 'min':
                    result[target_column] = numeric_df.min(axis=1)
                elif aggregate_function == 'max':
                    result[target_column] = numeric_df.max(axis=1)
                elif aggregate_function == 'median':
                    result[target_column] = numeric_df.median(axis=1)
                elif aggregate_function == 'std':
                    result[target_column] = numeric_df.std(axis=1)
                elif aggregate_function == 'var':
                    result[target_column] = numeric_df.var(axis=1)
                elif aggregate_function == 'prod':
                    result[target_column] = numeric_df.prod(axis=1)
                
        except Exception as e:
            raise ValueError(f"Error performing math operation: {str(e)}")
            
        return result
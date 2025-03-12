"""
Date Transformers
----------------
Plugin with date and time transformation operations.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from src.plugins.data_transformers import DataTransformer, register_transformer

@register_transformer
class DateFormatTransformer(DataTransformer):
    """
    Transformer to format dates in a column.
    """
    
    @property
    def name(self) -> str:
        return "Date Format Transformer"
        
    @property
    def description(self) -> str:
        return "Convert or format dates in a column"
        
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
                'name': 'input_format',
                'type': 'string',
                'label': 'Input Format (leave blank for auto-detect)',
                'required': False,
                'default': '',
                'help': "e.g., '%Y-%m-%d' for YYYY-MM-DD"
            },
            {
                'name': 'output_format',
                'type': 'select',
                'label': 'Output Format',
                'required': True,
                'default': '%Y-%m-%d',
                'options': [
                    {'value': '%Y-%m-%d', 'label': 'YYYY-MM-DD'},
                    {'value': '%m/%d/%Y', 'label': 'MM/DD/YYYY'},
                    {'value': '%d/%m/%Y', 'label': 'DD/MM/YYYY'},
                    {'value': '%b %d, %Y', 'label': 'Month DD, YYYY'},
                    {'value': '%B %d, %Y', 'label': 'Full Month DD, YYYY'},
                    {'value': '%Y%m%d', 'label': 'YYYYMMDD (no separators)'},
                    {'value': 'custom', 'label': 'Custom Format...'}
                ]
            },
            {
                'name': 'custom_output_format',
                'type': 'string',
                'label': 'Custom Output Format',
                'required': False,
                'default': '',
                'help': "Only used if 'Custom Format' is selected above"
            },
            {
                'name': 'create_new_column',
                'type': 'boolean',
                'label': 'Create New Column',
                'required': False,
                'default': False
            },
            {
                'name': 'new_column_name',
                'type': 'string',
                'label': 'New Column Name',
                'required': False,
                'default': '',
                'help': "Only used if 'Create New Column' is checked"
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Format dates in a column."""
        result = df.copy()
        
        column = params.get('column')
        input_format = params.get('input_format', '')
        output_format = params.get('output_format')
        custom_output_format = params.get('custom_output_format', '')
        create_new_column = params.get('create_new_column', False)
        new_column_name = params.get('new_column_name', '')
        
        if column not in result.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
            
        # Determine the actual output format
        if output_format == 'custom':
            if not custom_output_format:
                raise ValueError("Custom output format cannot be empty")
            actual_output_format = custom_output_format
        else:
            actual_output_format = output_format
            
        # Determine the target column
        target_column = new_column_name if create_new_column and new_column_name else column
        
        # Convert to datetime with the specified format or auto-detect
        try:
            if input_format:
                datetime_series = pd.to_datetime(result[column], format=input_format, errors='coerce')
            else:
                datetime_series = pd.to_datetime(result[column], infer_datetime_format=True, errors='coerce')
                
            # Format the dates
            formatted_dates = datetime_series.dt.strftime(actual_output_format)
            
            # Replace NaT with empty string
            formatted_dates = formatted_dates.fillna('')
            
            # Assign to the target column
            result[target_column] = formatted_dates
            
        except Exception as e:
            raise ValueError(f"Error formatting dates: {str(e)}")
            
        return result


@register_transformer
class DateExtractTransformer(DataTransformer):
    """
    Transformer to extract components from dates.
    """
    
    @property
    def name(self) -> str:
        return "Date Component Extractor"
        
    @property
    def description(self) -> str:
        return "Extract components (year, month, day, etc.) from dates"
        
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'column',
                'type': 'select',
                'label': 'Date Column',
                'required': True,
                'dynamic_options': True
            },
            {
                'name': 'component',
                'type': 'select',
                'label': 'Component to Extract',
                'required': True,
                'default': 'year',
                'options': [
                    {'value': 'year', 'label': 'Year'},
                    {'value': 'month', 'label': 'Month (number)'},
                    {'value': 'month_name', 'label': 'Month Name'},
                    {'value': 'day', 'label': 'Day of Month'},
                    {'value': 'day_of_week', 'label': 'Day of Week (number)'},
                    {'value': 'day_name', 'label': 'Day Name'},
                    {'value': 'quarter', 'label': 'Quarter'},
                    {'value': 'week', 'label': 'Week of Year'},
                    {'value': 'hour', 'label': 'Hour'},
                    {'value': 'minute', 'label': 'Minute'},
                    {'value': 'second', 'label': 'Second'}
                ]
            },
            {
                'name': 'target_column',
                'type': 'string',
                'label': 'Target Column Name',
                'required': True,
                'default': ''
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Extract date components."""
        result = df.copy()
        
        column = params.get('column')
        component = params.get('component')
        target_column = params.get('target_column')
        
        if column not in result.columns:
            raise ValueError(f"Column '{column}' not found in dataframe")
            
        if not target_column:
            raise ValueError("Target column name cannot be empty")
            
        # Convert to datetime
        try:
            datetime_series = pd.to_datetime(result[column], errors='coerce')
            
            # Extract the requested component
            if component == 'year':
                result[target_column] = datetime_series.dt.year
            elif component == 'month':
                result[target_column] = datetime_series.dt.month
            elif component == 'month_name':
                result[target_column] = datetime_series.dt.strftime('%B')
            elif component == 'day':
                result[target_column] = datetime_series.dt.day
            elif component == 'day_of_week':
                result[target_column] = datetime_series.dt.dayofweek + 1  # 1-based day of week
            elif component == 'day_name':
                result[target_column] = datetime_series.dt.strftime('%A')
            elif component == 'quarter':
                result[target_column] = datetime_series.dt.quarter
            elif component == 'week':
                result[target_column] = datetime_series.dt.isocalendar().week
            elif component == 'hour':
                result[target_column] = datetime_series.dt.hour
            elif component == 'minute':
                result[target_column] = datetime_series.dt.minute
            elif component == 'second':
                result[target_column] = datetime_series.dt.second
                
        except Exception as e:
            raise ValueError(f"Error extracting date components: {str(e)}")
            
        return result


@register_transformer
class DateDifferenceTransformer(DataTransformer):
    """
    Transformer to calculate the difference between two date columns.
    """
    
    @property
    def name(self) -> str:
        return "Date Difference Calculator"
        
    @property
    def description(self) -> str:
        return "Calculate the difference between two date columns"
        
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'start_column',
                'type': 'select',
                'label': 'Start Date Column',
                'required': True,
                'dynamic_options': True
            },
            {
                'name': 'end_column',
                'type': 'select',
                'label': 'End Date Column',
                'required': True,
                'dynamic_options': True
            },
            {
                'name': 'target_column',
                'type': 'string',
                'label': 'Target Column Name',
                'required': True,
                'default': 'date_difference'
            },
            {
                'name': 'unit',
                'type': 'select',
                'label': 'Time Unit',
                'required': True,
                'default': 'days',
                'options': [
                    {'value': 'days', 'label': 'Days'},
                    {'value': 'hours', 'label': 'Hours'},
                    {'value': 'minutes', 'label': 'Minutes'},
                    {'value': 'seconds', 'label': 'Seconds'},
                    {'value': 'weeks', 'label': 'Weeks'},
                    {'value': 'months', 'label': 'Months (approx)'},
                    {'value': 'years', 'label': 'Years (approx)'}
                ]
            },
            {
                'name': 'absolute_value',
                'type': 'boolean',
                'label': 'Use Absolute Value',
                'required': False,
                'default': False,
                'help': "If checked, negative differences will be converted to positive"
            }
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Calculate the difference between two date columns."""
        result = df.copy()
        
        start_column = params.get('start_column')
        end_column = params.get('end_column')
        target_column = params.get('target_column')
        unit = params.get('unit', 'days')
        absolute_value = params.get('absolute_value', False)
        
        if start_column not in result.columns:
            raise ValueError(f"Start column '{start_column}' not found in dataframe")
            
        if end_column not in result.columns:
            raise ValueError(f"End column '{end_column}' not found in dataframe")
            
        if not target_column:
            raise ValueError("Target column name cannot be empty")
            
        try:
            # Convert both columns to datetime
            start_dates = pd.to_datetime(result[start_column], errors='coerce')
            end_dates = pd.to_datetime(result[end_column], errors='coerce')
            
            # Calculate the difference
            diff = end_dates - start_dates
            
            # Convert to the requested unit
            if unit == 'days':
                result[target_column] = diff.dt.total_seconds() / (60 * 60 * 24)
            elif unit == 'hours':
                result[target_column] = diff.dt.total_seconds() / (60 * 60)
            elif unit == 'minutes':
                result[target_column] = diff.dt.total_seconds() / 60
            elif unit == 'seconds':
                result[target_column] = diff.dt.total_seconds()
            elif unit == 'weeks':
                result[target_column] = diff.dt.total_seconds() / (60 * 60 * 24 * 7)
            elif unit == 'months':
                result[target_column] = diff.dt.total_seconds() / (60 * 60 * 24 * 30.44)  # Average month length
            elif unit == 'years':
                result[target_column] = diff.dt.total_seconds() / (60 * 60 * 24 * 365.25)  # Average year length
                
            # Apply absolute value if requested
            if absolute_value:
                result[target_column] = result[target_column].abs()
                
            # Round to 2 decimal places for readability
            result[target_column] = result[target_column].round(2)
            
        except Exception as e:
            raise ValueError(f"Error calculating date difference: {str(e)}")
            
        return result
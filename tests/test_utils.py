"""
Tests for utility functions in the application.
"""

import unittest
import pandas as pd
import numpy as np
import io
import json
from unittest.mock import MagicMock, patch
import sys
import os
import base64

# Add the parent directory to the path so we can import the application modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.data_processors import (
    clean_dataframe,
    detect_duplicates,
    suggest_column_mapping,
    create_calculated_column,
    apply_data_transformations
)
from src.utils.file_handlers import (
    get_file_info,
    detect_encoding,
    read_file,
    get_download_link_multi_format
)

class TestDataProcessors(unittest.TestCase):
    """Test cases for data processing utility functions."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample DataFrame for testing
        self.df = pd.DataFrame({
            'ID': [1, 2, 3, 4, 5],
            'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
            'Age': [25, 30, np.nan, 40, 35],
            'City': ['New York', 'London', 'Paris', np.nan, 'Tokyo'],
            'Salary': [50000, 60000, 70000, 80000, np.nan]
        })
        
        # Create DataFrame with duplicates
        self.df_with_dupes = pd.DataFrame({
            'ID': [1, 2, 3, 3, 4],
            'Name': ['Alice', 'Bob', 'Charlie', 'Charlie', 'David'],
            'Value': [100, 200, 300, 300, 400]
        })
        
    def test_clean_dataframe_lowercase_columns(self):
        """Test clean_dataframe with lowercase column option."""
        options = {
            'ignore_case': True
        }
        
        result = clean_dataframe(self.df, options)
        
        # Check that all column names are lowercase
        for col in result.columns:
            self.assertEqual(col, col.lower())
            
    def test_clean_dataframe_fill_missing_zero(self):
        """Test clean_dataframe with fill missing values as zero."""
        options = {
            'fill_method': 'Zero'
        }
        
        result = clean_dataframe(self.df, options)
        
        # Check that there are no missing values
        self.assertEqual(result.isna().sum().sum(), 0)
        
        # Check that missing values were filled with 0
        self.assertEqual(result.loc[2, 'Age'], 0)
        self.assertEqual(result.loc[3, 'City'], 0)
        self.assertEqual(result.loc[4, 'Salary'], 0)
        
    def test_clean_dataframe_fill_missing_mean(self):
        """Test clean_dataframe with fill missing values as mean."""
        options = {
            'fill_method': 'Mean'
        }
        
        result = clean_dataframe(self.df, options)
        
        # Check that numeric missing values were filled with mean
        self.assertEqual(result.loc[2, 'Age'], self.df['Age'].mean())
        self.assertEqual(result.loc[4, 'Salary'], self.df['Salary'].mean())
        
        # Non-numeric column should still have NaN
        self.assertTrue(pd.isna(result.loc[3, 'City']))
        
    def test_clean_dataframe_drop_duplicates(self):
        """Test clean_dataframe with drop duplicates option."""
        options = {
            'handle_duplicates': True
        }
        
        result = clean_dataframe(self.df_with_dupes, options)
        
        # Check that duplicates were removed
        self.assertEqual(len(result), 4)  # One duplicate should be removed
        
        # Check that only one row with ID=3 remains
        self.assertEqual(sum(result['ID'] == 3), 1)
        
    def test_detect_duplicates(self):
        """Test detect_duplicates function."""
        # Test with the DataFrame that has duplicates
        result = detect_duplicates(self.df_with_dupes)
        
        # Should find one duplicate
        self.assertEqual(result['duplicate_count'], 1)
        
        # The duplicate row should be the second occurrence of ID=3
        self.assertTrue((result['duplicate_rows']['ID'] == 3).all())
        
        # Test with specific subset
        result = detect_duplicates(self.df_with_dupes, subset=['ID'])
        self.assertEqual(result['duplicate_count'], 1)
        
        # Test with subset that has no duplicates
        result = detect_duplicates(self.df_with_dupes, subset=['Value'])
        self.assertEqual(result['duplicate_count'], 0)
        
    def test_suggest_column_mapping_single_column(self):
        """Test suggest_column_mapping with a single column."""
        source = 'id'
        target_columns = ['ID', 'Name', 'Age', 'ID_NUM', 'identifier']
        
        result = suggest_column_mapping(source, target_columns, threshold=0.5)
        
        # Should match 'ID' and 'identifier' but not others
        self.assertIn('ID', result)
        self.assertIn('identifier', result)
        self.assertIn('ID_NUM', result)
        self.assertNotIn('Name', result)
        self.assertNotIn('Age', result)
        
    def test_suggest_column_mapping_multiple_columns(self):
        """Test suggest_column_mapping with multiple columns."""
        source = ['id', 'name', 'age']
        target_columns = ['ID', 'Name', 'Age', 'ID_NUM', 'FULLNAME']
        
        result = suggest_column_mapping(source, target_columns, threshold=0.5)
        
        # Check mappings
        self.assertEqual(result.get('id'), 'ID')
        self.assertEqual(result.get('name'), 'Name')
        self.assertEqual(result.get('age'), 'Age')
        
    def test_create_calculated_column(self):
        """Test create_calculated_column function."""
        # Create a new column as a calculation of existing columns
        expression = 'Age * 1000 + Salary'
        result = create_calculated_column(self.df, 'Total', expression)
        
        # Check that the new column exists
        self.assertIn('Total', result.columns)
        
        # Check that the calculation is correct
        expected = self.df['Age'] * 1000 + self.df['Salary']
        pd.testing.assert_series_equal(result['Total'], expected, check_names=False)
        
    def test_apply_data_transformations(self):
        """Test apply_data_transformations function."""
        # Define a series of transformations
        transformations = [
            {
                'type': 'create_calculated_column',
                'params': {
                    'column_name': 'Age_Group',
                    'expression': 'np.where(Age < 30, "Young", "Adult")'
                }
            },
            {
                'type': 'convert_column_type',
                'params': {
                    'column': 'ID',
                    'type': 'string'
                }
            }
"""
Tests for the FileMerger controller.
"""

import unittest
import pandas as pd
import numpy as np
import io
from unittest.mock import MagicMock, patch
import sys
import os

# Add the parent directory to the path so we can import the application modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.controllers.file_merger import FileMerger

class TestFileMerger(unittest.TestCase):
    """Test cases for the FileMerger class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a mock config
        self.config = {
            "max_file_size_mb": 100,
            "export_formats": ["csv", "xlsx", "json"]
        }
        
        # Initialize the FileMerger with the mock config
        self.merger = FileMerger(self.config)
        
        # Create sample DataFrames for testing
        self.df1 = pd.DataFrame({
            'id': [1, 2, 3],
            'name': ['Alice', 'Bob', 'Charlie'],
            'age': [25, 30, 35]
        })
        
        self.df2 = pd.DataFrame({
            'id': [2, 3, 4],
            'city': ['New York', 'London', 'Paris'],
            'salary': [50000, 60000, 70000]
        })
        
        # Create a mock uploaded file
        self.mock_csv_file = MagicMock()
        self.mock_csv_file.name = 'test.csv'
        self.mock_csv_file.size = 1000
        self.mock_csv_file.read.return_value = self.df1.to_csv(index=False).encode('utf-8')
        self.mock_csv_file.seek = MagicMock()
        
        self.mock_excel_file = MagicMock()
        self.mock_excel_file.name = 'test.xlsx'
        self.mock_excel_file.size = 2000
        
        # Create a buffer for Excel data
        excel_buffer = io.BytesIO()
        self.df2.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        self.mock_excel_file.read.return_value = excel_buffer.read()
        self.mock_excel_file.seek = MagicMock()
        
    def test_init(self):
        """Test initialization of FileMerger."""
        self.assertEqual(self.merger.max_file_size_mb, 100)
        self.assertEqual(self.merger.export_formats, ["csv", "xlsx", "json"])
        self.assertIn('csv', self.merger.supported_formats)
        self.assertIn('xlsx', self.merger.supported_formats)
        self.assertIn('json', self.merger.supported_formats)
        
    @patch('src.utils.file_handlers.get_file_info')
    @patch('src.utils.file_handlers.detect_encoding')
    @patch('src.utils.file_handlers.read_file')
    def test_load_data_csv(self, mock_read_file, mock_detect_encoding, mock_get_file_info):
        """Test loading CSV data."""
        # Set up mocks
        mock_get_file_info.return_value = {
            'name': 'test.csv',
            'type': 'text/csv',
            'size': 1000,
            'extension': 'csv'
        }
        mock_detect_encoding.return_value = 'utf-8'
        mock_read_file.return_value = self.df1
        
        # Call the method
        df, error = self.merger.load_data(self.mock_csv_file)
        
        # Assertions
        self.assertIsNone(error)
        self.assertIsInstance(df, pd.DataFrame)
        pd.testing.assert_frame_equal(df, self.df1)
        mock_get_file_info.assert_called_once_with(self.mock_csv_file)
        mock_detect_encoding.assert_called_once_with(self.mock_csv_file)
        mock_read_file.assert_called_once_with(
            self.mock_csv_file, 'csv', encoding='utf-8'
        )
        
    @patch('src.utils.file_handlers.get_file_info')
    @patch('src.utils.file_handlers.read_file')
    def test_load_data_excel(self, mock_read_file, mock_get_file_info):
        """Test loading Excel data."""
        # Set up mocks
        mock_get_file_info.return_value = {
            'name': 'test.xlsx',
            'type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'size': 2000,
            'extension': 'xlsx'
        }
        mock_read_file.return_value = self.df2
        
        # Call the method
        df, error = self.merger.load_data(self.mock_excel_file)
        
        # Assertions
        self.assertIsNone(error)
        self.assertIsInstance(df, pd.DataFrame)
        pd.testing.assert_frame_equal(df, self.df2)
        mock_get_file_info.assert_called_once_with(self.mock_excel_file)
        mock_read_file.assert_called_once()
        
    def test_load_data_unsupported_format(self):
        """Test loading an unsupported file format."""
        # Create a mock file with unsupported extension
        mock_file = MagicMock()
        mock_file.name = 'test.txt'
        mock_file.size = 500
        
        # Call the method
        df, error = self.merger.load_data(mock_file)
        
        # Assertions
        self.assertIsNone(df)
        self.assertIsNotNone(error)
        self.assertIn("Unsupported file format", error)
        
    def test_load_data_file_too_large(self):
        """Test loading a file that exceeds the size limit."""
        # Create a mock file that's too large
        mock_file = MagicMock()
        mock_file.name = 'large.csv'
        mock_file.size = (self.config["max_file_size_mb"] + 1) * 1024 * 1024
        
        # Call the method
        df, error = self.merger.load_data(mock_file)
        
        # Assertions
        self.assertIsNone(df)
        self.assertIsNotNone(error)
        self.assertIn("exceeds the maximum allowed size", error)
        
    @patch('src.controllers.file_merger.clean_dataframe')
    def test_process_files_append(self, mock_clean_dataframe):
        """Test processing files with append merge method."""
        # Set up mock for clean_dataframe to return the same dataframe
        mock_clean_dataframe.side_effect = lambda df, options: df
        
        # Mock the load_data method to return our test dataframes
        self.merger.load_data = MagicMock()
        self.merger.load_data.side_effect = [(self.df1, None), (self.df2, None)]
        
        # Create mock uploaded files
        mock_files = [self.mock_csv_file, self.mock_excel_file]
        
        # Create options
        options = {
            "merge_method": "Append (stack vertically)",
            "join_key": None,
            "join_type": "outer",
            "matching_columns": False,
            "output_filename": "test_output",
            "ignore_case": True,
            "handle_duplicates": False,
            "fill_missing": False,
            "fill_method": None,
            "fill_value": None
        }
        
        # Call the method
        result_df, errors = self.merger.process_files(mock_files, options)
        
        # Assertions
        self.assertIsNone(errors)
        self.assertIsInstance(result_df, pd.DataFrame)
        self.assertEqual(len(result_df), len(self.df1) + len(self.df2))
        self.assertEqual(set(result_df.columns), set(self.df1.columns) | set(self.df2.columns))
        
    @patch('src.controllers.file_merger.clean_dataframe')
    def test_process_files_join(self, mock_clean_dataframe):
        """Test processing files with join merge method."""
        # Set up mock for clean_dataframe to return the same dataframe
        mock_clean_dataframe.side_effect = lambda df, options: df
        
        # Mock the load_data method to return our test dataframes
        self.merger.load_data = MagicMock()
        self.merger.load_data.side_effect = [(self.df1, None), (self.df2, None)]
        
        # Create mock uploaded files
        mock_files = [self.mock_csv_file, self.mock_excel_file]
        
        # Create options
        options = {
            "merge_method": "Join on key column (merge horizontally)",
            "join_key": "id",
            "join_type": "inner",
            "matching_columns": False,
            "output_filename": "test_output",
            "ignore_case": True,
            "handle_duplicates": False,
            "fill_missing": False,
            "fill_method": None,
            "fill_value": None
        }
        
        # Call the method
        result_df, errors = self.merger.process_files(mock_files, options)
        
        # Assertions
        self.assertIsNone(errors)
        self.assertIsInstance(result_df, pd.DataFrame)
        # Should only contain rows with matching ids (2 and 3)
        self.assertEqual(len(result_df), 2)
        # Should contain columns from both dataframes
        self.assertEqual(
            set(result_df.columns), 
            set(self.df1.columns) | set(self.df2.columns)
        )
        
    def test_process_files_no_files(self):
        """Test processing with no files."""
        # Call the method with empty list
        result_df, errors = self.merger.process_files([], {})
        
        # Assertions
        self.assertIsNone(result_df)
        self.assertIsNotNone(errors)
        self.assertIn("No files uploaded", errors)
        
    def test_process_files_missing_join_key(self):
        """Test processing with join method but missing join key."""
        # Create options with join method but no key
        options = {
            "merge_method": "Join on key column (merge horizontally)",
            "join_key": None,
            "join_type": "inner"
        }
        
        # Call the method with mock files
        result_df, errors = self.merger.process_files(
            [self.mock_csv_file, self.mock_excel_file], 
            options
        )
        
        # Assertions
        self.assertIsNone(result_df)
        self.assertIsNotNone(errors)
        self.assertIn("Please specify a key column for joining", errors)

if __name__ == '__main__':
    unittest.main()
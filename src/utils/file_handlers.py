"""
File Handlers
------------
Utility functions for handling file operations.
"""

import pandas as pd
import json
import io
import base64
import chardet
from typing import Dict, List, Optional, Union, Tuple
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def get_file_info(uploaded_file) -> Dict:
    """
    Get information about an uploaded file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        Dictionary with file information
    """
    return {
        "name": uploaded_file.name,
        "type": uploaded_file.type,
        "size": uploaded_file.size,
        "extension": Path(uploaded_file.name).suffix.lower().lstrip('.')
    }

def detect_encoding(uploaded_file, sample_size: int = 10000) -> str:
    """
    Detect the encoding of a file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        sample_size: Number of bytes to sample for detection
        
    Returns:
        Detected encoding as string (defaults to utf-8 if detection fails)
    """
    try:
        # Save current position
        pos = uploaded_file.tell()
        
        # Read a sample of the file
        sample = uploaded_file.read(sample_size)
        
        # Reset position
        uploaded_file.seek(pos)
        
        # Detect encoding
        result = chardet.detect(sample)
        encoding = result['encoding']
        
        # If confidence is low or encoding is None, use utf-8
        if encoding is None or result['confidence'] < 0.7:
            encoding = 'utf-8'
            
        return encoding
    except Exception as e:
        logger.warning(f"Error detecting encoding: {str(e)}. Using utf-8 as fallback.")
        return 'utf-8'

def read_file(uploaded_file, file_extension: str, **kwargs) -> Optional[pd.DataFrame]:
    """
    Read a file into a pandas DataFrame based on its extension.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        file_extension: File extension (csv, xlsx, etc.)
        **kwargs: Additional arguments to pass to the reader function
        
    Returns:
        DataFrame if successfully loaded, None otherwise
    """
    try:
        if file_extension == 'csv':
            # For CSV, try to detect delimiter if not specified
            if 'delimiter' not in kwargs and 'sep' not in kwargs:
                sample = uploaded_file.read(4096).decode(kwargs.get('encoding', 'utf-8'))
                uploaded_file.seek(0)
                
                # Simple delimiter detection
                potential_delimiters = [',', ';', '\t', '|']
                delimiter_counts = {d: sample.count(d) for d in potential_delimiters}
                likely_delimiter = max(delimiter_counts, key=delimiter_counts.get)
                
                # Only use detected delimiter if it appears reasonably often
                if delimiter_counts[likely_delimiter] > 5:
                    kwargs['sep'] = likely_delimiter
                    
            return pd.read_csv(uploaded_file, **kwargs)
            
        elif file_extension in ['xlsx', 'xls']:
            return pd.read_excel(uploaded_file, **kwargs)
            
        elif file_extension == 'json':
            # Handle different JSON structures
            try:
                # Try direct loading first
                return pd.read_json(uploaded_file, **kwargs)
            except ValueError:
                # If direct loading fails, try manual parsing
                uploaded_file.seek(0)
                content = json.load(uploaded_file)
                
                # Determine if it's a list or dict and convert accordingly
                if isinstance(content, list):
                    return pd.json_normalize(content)
                elif isinstance(content, dict):
                    # Try different approaches based on JSON structure
                    if any(isinstance(v, list) for v in content.values()):
                        # Find the first list and normalize it
                        for k, v in content.items():
                            if isinstance(v, list):
                                return pd.json_normalize(v)
                    else:
                        # Convert flat dict to single-row DataFrame
                        return pd.DataFrame([content])
                
                # If all else fails
                raise ValueError("Unsupported JSON structure")
                
        else:
            logger.error(f"Unsupported file extension: {file_extension}")
            return None
            
    except Exception as e:
        logger.error(f"Error reading file: {str(e)}", exc_info=True)
        raise

def get_download_link_multi_format(
    df: pd.DataFrame, 
    filename: str = "data", 
    formats: List[str] = ["csv", "xlsx", "json"],
    auto_download: bool = False
) -> Dict[str, str]:
    """
    Generate download links for a dataframe in multiple formats.
    
    Args:
        df: Pandas DataFrame to export
        filename: Base filename without extension
        formats: List of formats to generate links for
        auto_download: Whether to generate auto-download script
        
    Returns:
        Dictionary with format keys and HTML link/script values
    """
    result = {}
    
    for fmt in formats:
        if fmt == "csv":
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            
            if auto_download:
                # Auto-download script
                result[fmt] = f"""
                <script>
                const link = document.createElement('a');
                link.href = 'data:file/csv;base64,{b64}';
                link.download = '{filename}.csv';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                </script>
                """
            else:
                # Download link
                href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv" class="download-button">Download CSV</a>'
                result[fmt] = href
                
        elif fmt == "xlsx":
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Data')
                
                # Access the XlsxWriter workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Data']
                
                # Add a header format
                header_format = workbook.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'bg_color': '#D9E1F2',
                    'border': 1
                })
                
                # Apply the header format
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    
                # Auto-fit columns
                for i, col in enumerate(df.columns):
                    max_width = max(
                        df[col].astype(str).map(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.set_column(i, i, max_width)
            
            b64 = base64.b64encode(output.getvalue()).decode()
            
            if auto_download:
                # Auto-download script
                result[fmt] = f"""
                <script>
                const link = document.createElement('a');
                link.href = 'data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}';
                link.download = '{filename}.xlsx';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                </script>
                """
            else:
                # Download link
                href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}.xlsx" class="download-button">Download Excel</a>'
                result[fmt] = href
                
        elif fmt == "json":
            json_str = df.to_json(orient='records', date_format='iso')
            b64 = base64.b64encode(json_str.encode()).decode()
            
            if auto_download:
                # Auto-download script
                result[fmt] = f"""
                <script>
                const link = document.createElement('a');
                link.href = 'data:application/json;base64,{b64}';
                link.download = '{filename}.json';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                </script>
                """
            else:
                # Download link
                href = f'<a href="data:application/json;base64,{b64}" download="{filename}.json" class="download-button">Download JSON</a>'
                result[fmt] = href
                
    return result
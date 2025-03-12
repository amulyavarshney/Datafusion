"""
File Merger Controller
---------------------
Controller for handling file merging operations with advanced options.
"""

import streamlit as st
import pandas as pd
import numpy as np
import base64
import json
from datetime import datetime
import io
from typing import List, Dict, Tuple, Optional, Any, Union
import logging
from pathlib import Path

from src.controllers.base_controller import BaseController
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

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FileMerger(BaseController):
    """
    Controller for merging multiple files with advanced options.
    
    Features:
    - Multiple file formats (CSV, Excel, JSON)
    - Multiple merging methods (append, join)
    - Data cleaning and transformation
    - Export to multiple formats
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize the FileMerger controller.
        
        Args:
            config: Configuration dictionary with app settings
        """
        super().__init__()
        self.config = config or {}
        self.max_file_size_mb = self.config.get("max_file_size_mb", 100)
        self.supported_formats = {
            'csv': 'CSV File',
            'xlsx': 'Excel File (XLSX)',
            'xls': 'Excel File (XLS)',
            'json': 'JSON File'
        }
        self.export_formats = self.config.get("export_formats", ["csv", "xlsx", "json"])
        
        # Initialize session state variables if needed
        if 'loaded_files' not in st.session_state:
            st.session_state.loaded_files = {}
        if 'merged_df' not in st.session_state:
            st.session_state.merged_df = None
        if 'last_merge_time' not in st.session_state:
            st.session_state.last_merge_time = None
            
    def load_data(self, uploaded_file) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
        """
        Load data from an uploaded file with advanced error handling and options.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            
        Returns:
            Tuple containing:
                - DataFrame if successfully loaded, None otherwise
                - Error message string if failed, None otherwise
        """
        # Check file size
        if uploaded_file.size > (self.max_file_size_mb * 1024 * 1024):
            return None, f"File {uploaded_file.name} exceeds the maximum allowed size of {self.max_file_size_mb}MB."
        
        # Get file extension
        file_extension = Path(uploaded_file.name).suffix.lower().lstrip('.')
        
        if file_extension not in self.supported_formats:
            return None, f"Unsupported file format: {file_extension}. Supported formats: {', '.join(self.supported_formats.keys())}"
        
        try:
            # Get file info and detect encoding for CSV files
            file_info = get_file_info(uploaded_file)
            
            # For CSV files, try to detect encoding
            encoding = None
            if file_extension == 'csv':
                encoding = detect_encoding(uploaded_file)
                
            # Read the file with appropriate parameters
            df = read_file(uploaded_file, file_extension, encoding=encoding)
            
            if df is None or df.empty:
                return None, f"File {uploaded_file.name} is empty or could not be read."
                
            # Log success
            logger.info(f"Successfully loaded file {uploaded_file.name} with {df.shape[0]} rows and {df.shape[1]} columns")
            
            return df, None
            
        except Exception as e:
            logger.error(f"Error loading file {uploaded_file.name}: {str(e)}", exc_info=True)
            return None, f"Error loading file {uploaded_file.name}: {str(e)}"
            
    def render_file_uploader(self):
        """Render the file uploader section with supported file types info."""
        st.subheader("Upload Files")
        
        # Show supported file types
        format_info = ", ".join([f"{ext.upper()} ({desc})" for ext, desc in self.supported_formats.items()])
        st.write(f"Supported formats: {format_info}")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Choose files to merge",
            type=list(self.supported_formats.keys()),
            accept_multiple_files=True,
            help="You can upload multiple files of different formats. Each file should have a proper header row."
        )
        
        if not uploaded_files:
            st.info("Please upload at least one file to begin.")
            with st.expander("Upload Tips"):
                st.markdown("""
                - Files should have consistent column naming for best results
                - Large files (>50MB) may take longer to process
                - For CSV files with non-standard formats, you can specify delimiter and encoding in the advanced options
                """)
            return None
            
        return uploaded_files
        
    def render_merge_options(self):
        """Render merge options section with advanced settings."""
        st.subheader("Merge Options")
        
        # Basic merge method
        merge_method = st.radio(
            "How would you like to merge files?",
            ["Append (stack vertically)", "Join on key column (merge horizontally)", "Smart merge (auto-detect)"],
            index=0 if self.config.get("default_merge_method") == "append" else 1,
            help="Append will stack files on top of each other. Join will merge files side by side based on a key column."
        )
        
        join_key = None
        join_type = 'outer'
        matching_columns = False
        
        # Additional options based on merge method
        if merge_method.startswith("Join"):
            col1, col2 = st.columns(2)
            
            with col1:
                join_key = st.text_input(
                    "Enter the name of the key column for joining",
                    help="This column should exist in all files with unique values for proper joining"
                )
                
            with col2:
                join_type = st.selectbox(
                    "Join type",
                    ["outer (keep all rows)", "inner (keep only matching rows)", "left (keep all rows from first file)"],
                    index=0,
                    help="Determines which rows to keep in the final result"
                )
                join_type = join_type.split(" ")[0]  # Extract the join type without the description
                
            matching_columns = st.checkbox(
                "Match columns with similar names",
                value=False,
                help="Enable fuzzy matching to handle slightly different column names across files"
            )
            
        elif merge_method.startswith("Smart"):
            st.info("Smart merge will attempt to automatically identify key columns and matching fields across files.")
            matching_threshold = st.slider(
                "Matching threshold (%)",
                min_value=50,
                max_value=100,
                value=80,
                help="Higher values require more exact matches"
            )
            
        # Advanced options in expander
        with st.expander("Advanced Options"):
            col1, col2 = st.columns(2)
            
            with col1:
                ignore_case = st.checkbox("Ignore case in column names", value=True)
                handle_duplicates = st.checkbox("Remove duplicate rows", value=False)
                
            with col2:
                fill_missing = st.checkbox("Fill missing values", value=False)
                if fill_missing:
                    fill_method = st.selectbox(
                        "Fill method",
                        ["None (keep NaN)", "Zero", "Mean", "Median", "Mode", "Forward fill", "Backward fill", "Custom value"]
                    )
                    
                    if fill_method == "Custom value":
                        fill_value = st.text_input("Custom fill value", "0")
                    else:
                        fill_value = None
                else:
                    fill_method = "None (keep NaN)"
                    fill_value = None
        
        # Output filename
        default_filename = f"merged_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        output_filename = st.text_input("Output filename (without extension)", default_filename)
        
        return {
            "merge_method": merge_method,
            "join_key": join_key,
            "join_type": join_type,
            "matching_columns": matching_columns,
            "output_filename": output_filename,
            "ignore_case": ignore_case if 'ignore_case' in locals() else True,
            "handle_duplicates": handle_duplicates if 'handle_duplicates' in locals() else False,
            "fill_missing": fill_missing if 'fill_missing' in locals() else False,
            "fill_method": fill_method if 'fill_method' in locals() else None,
            "fill_value": fill_value if 'fill_value' in locals() else None,
            "matching_threshold": matching_threshold if 'matching_threshold' in locals() else 80
        }
        
    def process_files(self, uploaded_files, options):
        """
        Process and merge the uploaded files based on the selected options.
        
        Args:
            uploaded_files: List of Streamlit UploadedFile objects
            options: Dictionary of merge options
            
        Returns:
            Tuple containing:
                - Merged DataFrame if successful, None otherwise
                - List of error messages
        """
        if not uploaded_files:
            return None, ["No files uploaded"]
            
        if options["merge_method"].startswith("Join") and not options["join_key"]:
            return None, ["Please specify a key column for joining"]
            
        # Load all files
        dfs = []
        file_names = []
        error_messages = []
        all_columns = set()
        
        with st.spinner("Loading and processing files..."):
            progress_bar = st.progress(0)
            
            for i, uploaded_file in enumerate(uploaded_files):
                # Update progress
                progress = (i + 1) / len(uploaded_files)
                progress_bar.progress(progress)
                
                # Load file
                df, error = self.load_data(uploaded_file)
                
                if error:
                    error_messages.append(error)
                    continue
                    
                if df is not None and not df.empty:
                    st.write(f"Loaded '{uploaded_file.name}' - {df.shape[0]} rows, {df.shape[1]} columns")
                    
                    # Handle column names case
                    if options["ignore_case"]:
                        df.columns = [col.lower() for col in df.columns]
                        if options["join_key"]:
                            options["join_key"] = options["join_key"].lower()
                            
                    # Check for join key if doing horizontal merge
                    if options["merge_method"].startswith("Join") and options["join_key"] not in df.columns:
                        error_messages.append(f"File '{uploaded_file.name}' is missing the key column '{options['join_key']}'")
                        
                        # Suggest similar columns
                        similar_cols = suggest_column_mapping(options["join_key"], df.columns)
                        if similar_cols:
                            suggestions = ", ".join([f"'{col}'" for col in similar_cols[:3]])
                            error_messages.append(f"  - Similar columns found: {suggestions}")
                            
                        continue
                        
                    # Store dataframe and metadata
                    dfs.append(df)
                    file_names.append(uploaded_file.name)
                    all_columns.update(df.columns)
                    
            # Clear progress bar
            progress_bar.empty()
            
        # Show errors if any
        if error_messages:
            return None, error_messages
            
        # Proceed if we have valid dataframes
        if len(dfs) > 0:
            # Apply data transformations and cleaning before merging
            for i, df in enumerate(dfs):
                # Fill missing values if requested
                if options["fill_missing"] and options["fill_method"] != "None (keep NaN)":
                    if options["fill_method"] == "Zero":
                        df = df.fillna(0)
                    elif options["fill_method"] == "Mean":
                        for col in df.select_dtypes(include=[np.number]).columns:
                            df[col] = df[col].fillna(df[col].mean())
                    elif options["fill_method"] == "Median":
                        for col in df.select_dtypes(include=[np.number]).columns:
                            df[col] = df[col].fillna(df[col].median())
                    elif options["fill_method"] == "Mode":
                        for col in df.columns:
                            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else np.nan)
                    elif options["fill_method"] == "Forward fill":
                        df = df.fillna(method='ffill')
                    elif options["fill_method"] == "Backward fill":
                        df = df.fillna(method='bfill')
                    elif options["fill_method"] == "Custom value":
                        try:
                            # Try to convert to numeric if possible
                            value = float(options["fill_value"]) if options["fill_value"].replace(".", "", 1).isdigit() else options["fill_value"]
                            df = df.fillna(value)
                        except:
                            df = df.fillna(options["fill_value"])
                
                # Handle duplicates if requested
                if options["handle_duplicates"]:
                    original_rows = len(df)
                    
                    # If joining, keep duplicates only in the key column
                    if options["merge_method"].startswith("Join") and options["join_key"] in df.columns:
                        df = df.drop_duplicates(subset=[options["join_key"]])
                    else:
                        df = df.drop_duplicates()
                        
                    dropped_rows = original_rows - len(df)
                    if dropped_rows > 0:
                        st.info(f"Removed {dropped_rows} duplicate rows from '{file_names[i]}'")
                        
                dfs[i] = df
                
            # Merge the dataframes
            st.subheader("Merging Files")
            
            if options["merge_method"] == "Append (stack vertically)":
                merged_df = pd.concat(dfs, ignore_index=True)
                st.success(f"Successfully merged {len(dfs)} files vertically. Result has {merged_df.shape[0]} rows and {merged_df.shape[1]} columns.")
                
            elif options["merge_method"] == "Join on key column (merge horizontally)":
                # Start with the first dataframe
                merged_df = dfs[0]
                
                # If column matching is enabled, preprocess column names
                if options["matching_columns"]:
                    st.info("Applying column name matching...")
                    
                    # Track original to matched column names
                    column_mappings = []
                    
                    # Process each dataframe after the first one
                    for i, df in enumerate(dfs[1:], 1):
                        mapping = suggest_column_mapping(
                            list(merged_df.columns),
                            list(df.columns),
                            threshold=options["matching_threshold"] / 100 if "matching_threshold" in options else 0.8
                        )
                        
                        # Rename columns according to mapping
                        rename_dict = {col2: col1 for col1, col2 in mapping.items() if col1 != col2}
                        if rename_dict:
                            df = df.rename(columns=rename_dict)
                            column_mappings.append({
                                "file": file_names[i],
                                "mappings": rename_dict
                            })
                            
                        dfs[i] = df
                        
                    # Show column mappings if any were made
                    if column_mappings:
                        with st.expander("Column Mappings Applied"):
                            for mapping in column_mappings:
                                st.write(f"**{mapping['file']}**:")
                                for orig, new in mapping["mappings"].items():
                                    st.write(f"  - '{orig}' → '{new}'")
                
                # Merge with each subsequent dataframe
                for i, df in enumerate(dfs[1:], 1):
                    merged_df = pd.merge(
                        merged_df,
                        df,
                        on=options["join_key"],
                        how=options["join_type"],
                        suffixes=(None, f"_{i}")
                    )
                    
                st.success(f"Successfully merged {len(dfs)} files horizontally on key '{options['join_key']}'. Result has {merged_df.shape[0]} rows and {merged_df.shape[1]} columns.")
                
            elif options["merge_method"] == "Smart merge (auto-detect)":
                st.info("Analyzing files for smart merge...")
                
                # If only one file, just use it directly
                if len(dfs) == 1:
                    merged_df = dfs[0]
                    st.success(f"Only one file provided. No merging needed.")
                    
                else:
                    # Detect common columns across all dataframes
                    common_cols = set.intersection(*[set(df.columns) for df in dfs])
                    
                    if not common_cols:
                        # No common columns - use append
                        merged_df = pd.concat(dfs, ignore_index=True)
                        st.warning("No common columns found across files. Performing vertical append instead.")
                        
                    else:
                        # Find potential key columns by checking uniqueness
                        potential_keys = []
                        for col in common_cols:
                            is_potential_key = True
                            for df in dfs:
                                # Check if column has unique values
                                if df[col].nunique() != len(df[col].dropna()):
                                    is_potential_key = False
                                    break
                            if is_potential_key:
                                potential_keys.append(col)
                                
                        if potential_keys:
                            # Use the first potential key found
                            key_col = potential_keys[0]
                            st.info(f"Automatically selected '{key_col}' as the key column for joining.")
                            
                            # Start with the first dataframe
                            merged_df = dfs[0]
                            
                            # Merge with each subsequent dataframe
                            for i, df in enumerate(dfs[1:], 1):
                                merged_df = pd.merge(
                                    merged_df,
                                    df,
                                    on=key_col,
                                    how='outer',
                                    suffixes=(None, f"_{i}")
                                )
                                
                            st.success(f"Successfully merged {len(dfs)} files using smart join on '{key_col}'. Result has {merged_df.shape[0]} rows and {merged_df.shape[1]} columns.")
                            
                        else:
                            # No unique key columns - use append
                            merged_df = pd.concat(dfs, ignore_index=True)
                            st.warning("No suitable key columns found. Performing vertical append instead.")
                
            # Save the merged dataframe in session state for later use
            st.session_state.merged_df = merged_df
            st.session_state.last_merge_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            return merged_df, None
            
        else:
            return None, ["No valid dataframes to merge"]
            
    def render_data_preview_and_download(self, df, output_filename):
        """
        Render a preview of the merged data and download options.
        
        Args:
            df: Merged pandas DataFrame
            output_filename: Base filename for downloads (without extension)
        """
        if df is not None and not df.empty:
            # Show preview of the merged data
            st.subheader("Preview of Merged Data")
            
            # Add a search/filter option
            search_term = st.text_input("Search/Filter data (searches all columns)", "")
            if search_term:
                mask = np.column_stack([df[col].astype(str).str.contains(search_term, case=False, na=False) for col in df.columns])
                filtered_df = df[mask.any(axis=1)]
                st.dataframe(filtered_df.head(10))
                st.info(f"Showing filtered preview. {len(filtered_df)} rows match the search term '{search_term}'.")
            else:
                st.dataframe(df.head(10))
                
            # Data summary with tabs
            st.subheader("Data Analysis")
            tab1, tab2, tab3 = st.tabs(["Column Information", "Data Types", "Missing Values"])
            
            with tab1:
                col_info = pd.DataFrame({
                    'Column Name': df.columns,
                    'Data Type': df.dtypes.astype(str),
                    'Non-Null Count': df.count().values,
                    'Null Count': df.isna().sum().values,
                    'Unique Values': [df[col].nunique() for col in df.columns]
                })
                st.dataframe(col_info)
                
            with tab2:
                # Group columns by data type
                type_groups = {}
                for col in df.columns:
                    col_type = str(df[col].dtype)
                    if col_type not in type_groups:
                        type_groups[col_type] = []
                    type_groups[col_type].append(col)
                
                for dtype, cols in type_groups.items():
                    with st.expander(f"{dtype} ({len(cols)} columns)"):
                        st.write(", ".join(cols))
                        
            with tab3:
                # Calculate missing values percentage
                missing_data = pd.DataFrame({
                    'Missing Values': df.isna().sum(),
                    'Percentage': (df.isna().sum() / len(df) * 100).round(2)
                }).sort_values('Percentage', ascending=False)
                
                missing_data = missing_data[missing_data['Missing Values'] > 0]
                
                if not missing_data.empty:
                    st.dataframe(missing_data)
                    
                    # Missing data visualization
                    st.write("Percentage of missing values by column:")
                    missing_chart_data = pd.DataFrame({
                        'Column': missing_data.index,
                        'Percentage': missing_data['Percentage']
                    })
                    st.bar_chart(missing_chart_data.set_index('Column'))
                else:
                    st.success("No missing values found in the dataset!")
                    
            # Data transformations
            with st.expander("Data Transformations"):
                st.write("Apply transformations to the merged data:")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    transformation_type = st.selectbox(
                        "Transformation type",
                        ["None", "Create calculated column", "Convert data types", "Replace values", "Filter rows"]
                    )
                    
                if transformation_type == "Create calculated column":
                    column_name = st.text_input("New column name")
                    column_expression = st.text_input("Expression (use column names as variables)", 
                                                    placeholder="e.g., column_a * column_b")
                    
                    if st.button("Add calculated column") and column_name and column_expression:
                        try:
                            new_df = create_calculated_column(df, column_name, column_expression)
                            st.session_state.merged_df = new_df
                            st.success(f"Created new column '{column_name}'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error creating calculated column: {str(e)}")
                            
                elif transformation_type == "Convert data types":
                    col_to_convert = st.selectbox("Select column to convert", df.columns)
                    target_type = st.selectbox("Convert to", ["string", "number", "datetime", "boolean"])
                    
                    if st.button("Convert column type"):
                        try:
                            new_df = df.copy()
                            if target_type == "string":
                                new_df[col_to_convert] = new_df[col_to_convert].astype(str)
                            elif target_type == "number":
                                new_df[col_to_convert] = pd.to_numeric(new_df[col_to_convert], errors='coerce')
                            elif target_type == "datetime":
                                new_df[col_to_convert] = pd.to_datetime(new_df[col_to_convert], errors='coerce')
                            elif target_type == "boolean":
                                new_df[col_to_convert] = new_df[col_to_convert].astype(bool)
                                
                            st.session_state.merged_df = new_df
                            st.success(f"Converted '{col_to_convert}' to {target_type}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error converting column type: {str(e)}")
                            
                elif transformation_type == "Replace values":
                    col_to_modify = st.selectbox("Select column", df.columns)
                    find_value = st.text_input("Find value")
                    replace_value = st.text_input("Replace with")
                    
                    if st.button("Replace values") and find_value:
                        try:
                            new_df = df.copy()
                            new_df[col_to_modify] = new_df[col_to_modify].replace(find_value, replace_value)
                            st.session_state.merged_df = new_df
                            st.success(f"Replaced values in '{col_to_modify}'")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error replacing values: {str(e)}")
                            
                elif transformation_type == "Filter rows":
                    filter_col = st.selectbox("Filter column", df.columns)
                    filter_type = st.selectbox("Filter type", ["equals", "not equals", "contains", "greater than", "less than"])
                    filter_value = st.text_input("Filter value")
                    
                    if st.button("Apply filter") and filter_value:
                        try:
                            new_df = df.copy()
                            
                            if filter_type == "equals":
                                new_df = new_df[new_df[filter_col] == filter_value]
                            elif filter_type == "not equals":
                                new_df = new_df[new_df[filter_col] != filter_value]
                            elif filter_type == "contains":
                                new_df = new_df[new_df[filter_col].astype(str).str.contains(filter_value, na=False)]
                            elif filter_type == "greater than":
                                new_df = new_df[pd.to_numeric(new_df[filter_col], errors='coerce') > float(filter_value)]
                            elif filter_type == "less than":
                                new_df = new_df[pd.to_numeric(new_df[filter_col], errors='coerce') < float(filter_value)]
                                
                            st.session_state.merged_df = new_df
                            st.success(f"Applied filter to '{filter_col}'. {len(new_df)} rows remaining.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error applying filter: {str(e)}")
                
            with col2:
                if transformation_type != "None":
                    st.info("Transformations will modify the merged dataset for download.")
                    
                # Reset transformations
                if st.button("Reset all transformations"):
                    if "original_merged_df" in st.session_state:
                        st.session_state.merged_df = st.session_state.original_merged_df.copy()
                        st.success("Reset all transformations")
                        st.rerun()
                    else:
                        st.warning("No original data to reset to")
                    
            # Download options
            st.subheader("Download Merged Data")
            
            # Export format options
            export_format = st.radio(
                "Select export format",
                options=[fmt.upper() for fmt in self.export_formats],
                horizontal=True
            )
            
            # Generate download links
            download_links = get_download_link_multi_format(
                df, 
                filename=output_filename,
                formats=[export_format.lower()]
            )
            
            # Display download button
            for fmt, link in download_links.items():
                st.markdown(link, unsafe_allow_html=True)
                
            # Add auto-download option
            auto_download = st.checkbox("Auto-download file", value=True)
            if auto_download:
                auto_link = get_download_link_multi_format(
                    df, 
                    filename=output_filename,
                    formats=[export_format.lower()],
                    auto_download=True
                )
                
                for fmt, script in auto_link.items():
                    st.markdown(script, unsafe_allow_html=True)
                    
            # Show download information
            with st.expander("Download Information"):
                st.write(f"Total records: {df.shape[0]}")
                st.write(f"Total columns: {df.shape[1]}")
                st.write(f"File name: {output_filename}.{export_format.lower()}")
                
                if export_format.lower() == "csv":
                    st.write("CSV files can be opened in Excel, Google Sheets, or any spreadsheet software.")
                elif export_format.lower() == "xlsx":
                    st.write("Excel files preserve formatting and can contain multiple sheets.")
                elif export_format.lower() == "json":
                    st.write("JSON format is ideal for web applications and APIs.")
        else:
            st.warning("No data to preview. Please upload and merge files first.")
            
    def handle(self):
        """Main handler method that orchestrates the entire workflow."""
        # Render header and description
        st.title("DataFusion: Advanced File Merger")
        st.markdown("""
        Merge multiple CSV, Excel, and JSON files with advanced options.
        Upload your files, configure merge options, and download the results.
        """)
        
        # Sidebar with latest merge info
        if st.session_state.last_merge_time:
            st.sidebar.success(f"Last merge: {st.session_state.last_merge_time}")
            
        # Upload files
        uploaded_files = self.render_file_uploader()
        
        if not uploaded_files:
            return
            
        # Store original files in session state if not already done
        if "loaded_files" not in st.session_state or not st.session_state.loaded_files:
            st.session_state.loaded_files = {file.name: file for file in uploaded_files}
            
        # Merge options
        options = self.render_merge_options()
        
        # Process files button
        col1, col2 = st.columns([3, 1])
        with col1:
            process_button = st.button("Merge Files", type="primary", use_container_width=True)
        with col2:
            reset_button = st.button("Reset", use_container_width=True)
            
        if reset_button:
            # Clear session state
            for key in ['loaded_files', 'merged_df', 'last_merge_time', 'original_merged_df']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
            
        if process_button:
            # Process and merge files
            merged_df, errors = self.process_files(uploaded_files, options)
            
            if errors:
                st.error("Encountered the following errors:")
                for msg in errors:
                    st.write(f"- {msg}")
                    
            if merged_df is not None:
                # Store original merged dataframe for reset functionality
                if "original_merged_df" not in st.session_state:
                    st.session_state.original_merged_df = merged_df.copy()
                    
                # Render preview and download options
                self.render_data_preview_and_download(merged_df, options["output_filename"])
        elif st.session_state.merged_df is not None:
            # If we already have a merged dataframe in session state, show it
            self.render_data_preview_and_download(st.session_state.merged_df, options["output_filename"])
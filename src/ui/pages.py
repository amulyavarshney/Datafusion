"""
UI Pages
-------
Page layouts for different sections of the application.
"""

import streamlit as st

def render_about_page():
    """Render the About page with information about the application."""
    st.title("About DataFusion")
    
    st.markdown("""
    ## Overview
    
    DataFusion is an advanced file merging application built with Streamlit and Pandas. 
    It allows you to merge multiple files of different formats with advanced options and transformations.
    
    ## Features
    
    - **Multiple File Support**: CSV, Excel, and JSON files
    - **Flexible Merging**: Append, join, and smart merge options
    - **Data Cleaning**: Handle missing values, duplicates, and more
    - **Transformations**: Create calculated columns, convert data types, filter rows
    - **Export Options**: Download in various formats
    
    ## How to Use
    
    1. **Upload Files**: Start by uploading one or more files
    2. **Configure Options**: Choose how to merge your files and set options
    3. **Process Data**: Click the "Merge Files" button to process your data
    4. **Transform**: Apply transformations to clean and enhance your data
    5. **Download**: Export the merged data in your preferred format
    
    ## Technical Details
    
    DataFusion is built with:
    
    - **Streamlit**: For the web interface
    - **Pandas**: For data processing
    - **Python**: Core programming language
    """)
    
    # Show application statistics
    st.subheader("Application Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Files Processed", len(st.session_state.get("loaded_files", {})))
        
    with col2:
        if "merged_df" in st.session_state and st.session_state.merged_df is not None:
            st.metric("Records Processed", st.session_state.merged_df.shape[0])
        else:
            st.metric("Records Processed", 0)
            
    # GitHub information
    st.subheader("GitHub Repository")
    
    st.markdown("""
    DataFusion is open source and available on GitHub. Feel free to contribute, report issues, or suggest features.
    
    [Visit GitHub Repository](https://github.com/amulyavarshney/datafusion)
    
    ## License
    
    This project is licensed under the MIT License - see the LICENSE file in the repository for details.
    """)
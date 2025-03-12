"""
UI Components
------------
Reusable UI components for the application.
"""

import streamlit as st
from datetime import datetime

def render_header():
    """
    Render the application header with navigation.
    
    Creates a navigation bar with links to different pages of the app.
    """
    # App title and logo
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.image("https://raw.githubusercontent.com/amulyavarshney/datafusion/main/docs/images/logo.png", width=80)
        
    with col2:
        st.title("DataFusion")
        
    # Navigation bar
    menu_items = {
        "merger": "File Merger",
        "about": "About"
    }
    
    # Create horizontal navigation menu
    cols = st.columns(len(menu_items))
    
    for i, (page_id, page_name) in enumerate(menu_items.items()):
        with cols[i]:
            if st.button(
                page_name,
                key=f"nav_{page_id}",
                use_container_width=True,
                type="primary" if st.session_state.page == page_id else "secondary"
            ):
                st.session_state.page = page_id
                st.rerun()
                
    # Divider
    st.markdown("---")
    
def render_sidebar(config):
    """
    Render the sidebar with app information and settings.
    
    Args:
        config: Application configuration dictionary
    """
    with st.sidebar:
        st.subheader("DataFusion")
        st.write("Version 1.0.0")
        
        # App statistics
        if "loaded_files" in st.session_state and st.session_state.loaded_files:
            st.write(f"Files loaded: {len(st.session_state.loaded_files)}")
            
        if "merged_df" in st.session_state and st.session_state.merged_df is not None:
            st.write(f"Merged dataset size: {st.session_state.merged_df.shape[0]} rows, {st.session_state.merged_df.shape[1]} columns")
            
        # Settings section
        st.subheader("Settings")
        
        # Theme selector
        theme = st.radio(
            "Theme",
            ["Light", "Dark"],
            index=0 if config.get("theme", "light") == "light" else 1,
            horizontal=True
        )
        
        if theme == "Dark" and config.get("theme") != "dark":
            config["theme"] = "dark"
            st.rerun()
        elif theme == "Light" and config.get("theme") != "light":
            config["theme"] = "light"
            st.rerun()
            
        # File size limit
        max_file_size = st.slider(
            "Max file size (MB)",
            min_value=10,
            max_value=500,
            value=config.get("max_file_size_mb", 100),
            step=10
        )
        
        if max_file_size != config.get("max_file_size_mb"):
            config["max_file_size_mb"] = max_file_size
            
        # Help section
        st.subheader("Help")
        
        with st.expander("Quick Tips"):
            st.markdown("""
            - **Upload multiple files** of different formats
            - Use **Append** to stack files vertically
            - Use **Join** to merge files side by side
            - **Smart merge** auto-detects the best way to combine
            - Apply **transformations** to clean and modify data
            - **Export formats** include CSV, Excel, and JSON
            """)
            
        # About the app
        st.markdown("---")
        st.write("© 2025 Amulya Varshney")
        st.write("[GitHub](https://github.com/amulyavarshney/datafusion) | [Documentation](https://github.com/amulyavarshney/datafusion/wiki)")
        
def render_footer():
    """Render the application footer."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("DataFusion © 2025")
        
    with col2:
        st.write(f"Current time: {datetime.now().strftime('%H:%M:%S')}")
        
    with col3:
        st.write("[Report Issues](https://github.com/amulyavarshney/datafusion/issues)")
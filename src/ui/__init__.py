"""
UI Package
---------
Contains UI components and page layouts for the DataFusion application.
"""

# Import components for easy access
from src.ui.components import (
    render_header,
    render_sidebar,
    render_footer
)

# Import pages
from src.ui.pages import (
    render_about_page
)

__all__ = [
    'render_header',
    'render_sidebar',
    'render_footer',
    'render_about_page'
]
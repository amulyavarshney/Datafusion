# DataFusion Project Structure

This document explains the organization and architecture of the DataFusion application.

## Core Architecture

DataFusion follows a Model-View-Controller (MVC) architecture:

- **Model**: Data processing utilities in the `utils` directory
- **View**: UI components in the `ui` directory
- **Controller**: Business logic in the `controllers` directory

## Directory Structure

```
datafusion/
├── app.py                      # Main application entry point
├── config.json                 # Configuration file
├── requirements.txt            # Project dependencies
├── LICENSE                     # MIT License
├── README.md                   # Project documentation
├── PROJECT_STRUCTURE.md        # This file
├── src/                        # Source code
│   ├── controllers/            # Business logic controllers
│   │   ├── __init__.py
│   │   ├── base_controller.py  # Abstract base controller
│   │   └── file_merger.py      # File merging controller
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── data_processors.py  # Data processing utilities
│   │   └── file_handlers.py    # File I/O utilities
│   ├── ui/                     # UI components
│   │   ├── __init__.py
│   │   ├── components.py       # Reusable UI components
│   │   └── pages.py            # Page layouts
│   └── plugins/                # Plugin system (extensibility)
│       ├── __init__.py
│       └── data_transformers/  # Custom data transformation plugins
├── tests/                      # Unit tests
│   ├── __init__.py
│   ├── test_file_merger.py
│   └── test_utils.py
└── examples/                   # Example files
    ├── sample1.csv
    ├── sample2.xlsx
    └── sample_config.json
```

## Key Components

### Controllers

Controllers handle the business logic of the application:

- **BaseController**: Abstract base class for all controllers
- **FileMerger**: Handles file merging operations with advanced options

### Utilities

Utility modules provide reusable functionality:

- **data_processors.py**: Functions for data processing and transformation
- **file_handlers.py**: Functions for file operations and handling

### UI Components

UI components handle the presentation layer:

- **components.py**: Reusable UI elements like headers, footers, and sidebars
- **pages.py**: Page layouts for different sections of the app

## Data Flow

1. User uploads files through the Streamlit interface
2. Files are read and validated by the file handlers
3. The controller processes the files based on user options
4. Data processors perform transformations as needed
5. Results are displayed in the UI and available for download

## Extension Points

The application is designed to be extensible in several ways:

1. **New File Formats**: Add support by extending `read_file()` in file_handlers.py
2. **New Transformations**: Add functions to data_processors.py
3. **New Controllers**: Create new controller classes inheriting from BaseController
4. **Plugins**: Add custom functionality through the plugin system

## Configuration

The application is configured through the `config.json` file with options for:

- UI theme and appearance
- File size limits
- Default merge methods
- Export formats
- Feature toggles
- Default data processing options

## Session State Management

Streamlit's session state is used to maintain application state between reruns:

- `st.session_state.page`: Current active page
- `st.session_state.loaded_files`: Dictionary of loaded files
- `st.session_state.merged_df`: Merged DataFrame
- `st.session_state.last_merge_time`: Timestamp of last merge operation
- `st.session_state.original_merged_df`: Original merged DataFrame (before transformations)

## Enhancements from Original Code

The enhanced application extends the original code with:

1. **Improved Architecture**: Modular, maintainable code structure
2. **Multiple File Formats**: Support for CSV, Excel, and JSON
3. **Advanced Merging Options**: Vertical stacking, horizontal joining, and smart merging
4. **Data Cleaning**: Options for handling missing values and duplicates
5. **Data Transformations**: Create calculated columns, convert data types, filter rows
6. **Enhanced UI**: Multi-page interface with navigation
7. **Improved Visualization**: Data previews and quality analysis
8. **Multiple Export Formats**: CSV, Excel, and JSON
9. **Extensibility**: Plugin system for custom functionality
10. **Configuration**: External configuration file for app settings
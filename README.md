# DataFusion: Advanced File Merger App

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://datafusion.streamlit.app/)

DataFusion is a powerful Streamlit application that allows users to merge multiple CSV and Excel files with advanced options and visualizations.

![DataFusion Screenshot](https://raw.githubusercontent.com/amulyavarshney/datafusion/main/docs/images/screenshot.png)

## Features

- **Multiple File Support**: Merge CSV, Excel (XLSX, XLS), and JSON files
- **Flexible Merging Options**:
  - Vertical stacking (append)
  - Horizontal joining on key columns
  - Smart column matching with fuzzy matching
  - Custom column mapping
- **Data Cleaning**:
  - Handle missing values (fill, drop, replace)
  - Remove duplicates
  - Data type conversion
- **Data Transformation**:
  - Filter rows based on conditions
  - Create calculated columns
  - Rename columns
- **Visualization**:
  - Preview merged data
  - Column statistics
  - Data quality report
- **Export Options**:
  - CSV, Excel, JSON formats
  - Configurable download options
- **Extensible Architecture**:
  - Plugin system for custom data processors
  - Support for additional file formats

## Installation

```bash
# Clone the repository
git clone https://github.com/amulyavarshney/datafusion.git
cd datafusion

# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

```bash
# Run the app
streamlit run app.py
```

Then open your browser and navigate to http://localhost:8501

## Project Structure

```
datafusion/
├── app.py                      # Main application entry point
├── requirements.txt            # Project dependencies
├── LICENSE                     # MIT License
├── README.md                   # This file
├── docs/                       # Documentation
│   └── images/                 # Screenshots and images
├── src/                        # Source code
│   ├── controllers/            # Business logic controllers
│   │   ├── __init__.py
│   │   ├── base_controller.py  # Base controller class
│   │   └── file_merger.py      # File merging controller
│   ├── utils/                  # Utility functions
│   │   ├── __init__.py
│   │   ├── data_processors.py  # Data processing utilities
│   │   └── file_handlers.py    # File I/O utilities
│   ├── ui/                     # UI components
│   │   ├── __init__.py
│   │   ├── components.py       # Reusable UI components
│   │   └── pages.py            # Page layouts
│   └── plugins/                # Plugin system for extensibility
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

## Configuration

You can customize the behavior of DataFusion using a configuration file:

```json
{
  "theme": "light",
  "max_file_size_mb": 100,
  "default_merge_method": "append",
  "plugins_enabled": true,
  "export_formats": ["csv", "xlsx", "json"]
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Streamlit](https://streamlit.io/) for the amazing app framework
- [Pandas](https://pandas.pydata.org/) for powerful data manipulation
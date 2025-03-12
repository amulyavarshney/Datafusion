# Configuration

DataFusion can be customized using the `config.json` file. This document explains all available configuration options.

## Configuration File Location

The configuration file should be placed in the root directory of the application:

```
datafusion/
├── app.py
├── config.json    <-- Configuration file
├── ...
```

## Configuration Format

The configuration file uses JSON format. Here's an example of a complete configuration:

```json
{
    "theme": "light",
    "max_file_size_mb": 100,
    "default_merge_method": "append",
    "plugins_enabled": true,
    "export_formats": ["csv", "xlsx", "json"],
    "ui": {
        "show_logo": true,
        "show_footer": true,
        "accent_color": "#4b8bbe"
    },
    "advanced_features": {
        "enable_transformations": true,
        "enable_data_preview": true,
        "enable_column_mapping": true,
        "enable_data_quality_analysis": true
    },
    "default_fill_methods": {
        "numeric": "mean",
        "categorical": "mode",
        "datetime": "forward_fill",
        "text": "empty_string"
    }
}
```

## Configuration Options

### Core Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `theme` | string | `"light"` | UI theme. Options: `"light"`, `"dark"` |
| `max_file_size_mb` | number | `100` | Maximum allowed file size in MB |
| `default_merge_method` | string | `"append"` | Default merge method. Options: `"append"`, `"join"` |
| `plugins_enabled` | boolean | `true` | Enable/disable the plugin system |
| `export_formats` | array | `["csv", "xlsx", "json"]` | Available export formats |

### UI Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `ui.show_logo` | boolean | `true` | Show/hide the application logo |
| `ui.show_footer` | boolean | `true` | Show/hide the footer |
| `ui.accent_color` | string | `"#4b8bbe"` | Primary accent color (hex code) |

### Advanced Features

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `advanced_features.enable_transformations` | boolean | `true` | Enable/disable data transformations |
| `advanced_features.enable_data_preview` | boolean | `true` | Enable/disable data preview |
| `advanced_features.enable_column_mapping` | boolean | `true` | Enable/disable column mapping |
| `advanced_features.enable_data_quality_analysis` | boolean | `true` | Enable/disable data quality analysis |

### Default Fill Methods

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `default_fill_methods.numeric` | string | `"mean"` | Default method for filling numeric missing values |
| `default_fill_methods.categorical` | string | `"mode"` | Default method for filling categorical missing values |
| `default_fill_methods.datetime` | string | `"forward_fill"` | Default method for filling datetime missing values |
| `default_fill_methods.text` | string | `"empty_string"` | Default method for filling text missing values |

## Creating a Custom Configuration

To customize the application:

1. Copy the example configuration above
2. Modify the options as needed
3. Save as `config.json` in the root directory
4. Restart the application for changes to take effect

## Environment-Specific Configuration

For different environments (development, testing, production), you can create multiple configuration files:

- `config.dev.json`
- `config.test.json`
- `config.prod.json`

To use a specific configuration:

```bash
# Set environment variable
export DATAFUSION_ENV=prod

# Run the application
streamlit run app.py
```

The application will automatically load `config.prod.json` if the environment variable is set.

## Dynamic Configuration

Some configuration options can be changed through the UI (in the sidebar):

- Theme (light/dark)
- Maximum file size

These changes will not persist between application restarts unless you update the `config.json` file.
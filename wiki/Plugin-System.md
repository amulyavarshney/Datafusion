# Plugin System

DataFusion includes a powerful plugin system that allows extending the application with custom functionality. This document explains how to create and use plugins.

## Plugin Types

DataFusion currently supports the following types of plugins:

1. **Data Transformers**: Add custom data transformation operations

Future versions may add support for:
- Custom file format handlers
- Custom export formats
- Custom visualization components

## Data Transformers

Data transformers allow you to add custom operations for processing and transforming data.

### Using Data Transformers

Data transformers are available in the "Data Transformations" section of the application after merging files. Each transformer provides a specific operation to modify your data.

### Creating a Custom Data Transformer

To create a custom data transformer:

1. Create a new Python file in the `src/plugins/data_transformers/` directory
2. Define a class that inherits from `DataTransformer`
3. Implement the required methods
4. Register the transformer using the `@register_transformer` decorator

Here's a template for a custom data transformer:

```python
from src.plugins.data_transformers import DataTransformer, register_transformer
import pandas as pd
from typing import Dict, Any, List

@register_transformer
class MyCustomTransformer(DataTransformer):
    """
    Description of your transformer.
    """
    
    @property
    def name(self) -> str:
        return "My Custom Transformer"
        
    @property
    def description(self) -> str:
        return "Description of what your transformer does"
        
    def get_parameters(self) -> List[Dict[str, Any]]:
        return [
            {
                'name': 'param1',
                'type': 'string',
                'label': 'Parameter 1',
                'required': True,
                'default': 'default value'
            },
            # Add more parameters as needed
        ]
        
    def transform(self, df: pd.DataFrame, params: Dict[str, Any]) -> pd.DataFrame:
        """Implement your transformation logic here."""
        result = df.copy()
        
        # Get parameters
        param1 = params.get('param1', 'default value')
        
        # Apply transformation
        # ... your transformation logic ...
        
        return result
```

### Parameter Types

Data transformers can define parameters with the following types:

- `string`: Text input
- `number`: Numeric input
- `boolean`: Checkbox
- `select`: Dropdown with options
- `select_multiple`: Multiple-select dropdown

For `select` and `select_multiple` types, you must provide an `options` list with `value` and `label` keys for each option.

### Dynamic Options

For parameters that should be populated with column names, set `dynamic_options: true` in the parameter definition. The application will automatically populate the options with column names from the current dataframe.

## Installing Plugins

To install a plugin:

1. Place the plugin file in the appropriate directory (e.g., `src/plugins/data_transformers/`)
2. Restart the application

The plugin will be automatically discovered and registered when the application starts.

## Example Plugins

DataFusion comes with several example plugins:

### Text Transformers

- **Text Case Transformer**: Change text case (upper, lower, title)
- **Text Pattern Extractor**: Extract text matching a regular expression
- **Text Replace Transformer**: Replace text using regular expressions

### Date Transformers

- **Date Format Transformer**: Format dates in a column
- **Date Component Extractor**: Extract year, month, day, etc. from dates
- **Date Difference Calculator**: Calculate time between dates

### Numeric Transformers

- **Numeric Scaling Transformer**: Scale numeric data (min-max, z-score)
- **Binning Transformer**: Create categories from numeric data
- **Math Operation Transformer**: Apply math operations to columns

## Creating Your Own Plugin Types

Advanced users can create entirely new types of plugins by:

1. Creating a new directory in the `src/plugins/` directory
2. Defining a base class for the plugin type
3. Implementing a registration mechanism
4. Updating the application to use the new plugin type

For more information, consult the source code of existing plugin types as a reference.
# Calculated Columns

One of DataFusion's powerful features is the ability to create calculated columns based on expressions. This allows you to derive new data from existing columns without the need for external processing.

## Creating a Calculated Column

To create a calculated column:

1. Merge your files using any merge method
2. In the "Data Transformations" section, expand the options
3. Select "Create calculated column" as the transformation type
4. Enter a name for your new column
5. Enter an expression that defines how to calculate the column
6. Click "Add calculated column"

## Expression Syntax

Expressions use Python syntax and can reference existing column names directly as variables.

### Basic Examples

Assuming you have columns named `price` and `quantity`:

- `price * quantity` - Multiply price by quantity
- `price - (price * 0.1)` - Price with 10% discount
- `(price > 100) * 1` - Returns 1 if price > 100, otherwise 0

### Available Operations

- **Arithmetic**: `+`, `-`, `*`, `/`, `**` (power), `%` (modulo)
- **Comparison**: `>`, `<`, `>=`, `<=`, `==`, `!=`
- **Logical**: `and`, `or`, `not`
- **Conditional**: Use `np.where(condition, value_if_true, value_if_false)`

### Using Functions

You can use numpy functions in your expressions. For example:

- `np.log(revenue)` - Natural logarithm of revenue
- `np.sqrt(area)` - Square root of area
- `np.sin(angle)` - Sine of angle
- `np.where(age > 18, 'Adult', 'Minor')` - Categorize based on age

### Column Names with Spaces

If your column names contain spaces or special characters, you can reference them using `df['column name']` in the expression:

- `df['Sale Price'] * df['Quantity Sold']`

## Examples

Here are some practical examples of calculated columns:

### Financial Calculations

- **Profit**: `revenue - cost`
- **Profit Margin**: `(revenue - cost) / revenue * 100`
- **Tax Amount**: `price * 0.07`  # 7% tax
- **Total with Tax**: `price * 1.07`

### Data Transformations

- **Normalize Value**: `(value - min_value) / (max_value - min_value)`
- **Z-Score**: `(value - mean) / std_dev`
- **Log Transform**: `np.log(value + 1)`  # Adding 1 to handle zeros

### Categorical Variables

- **Age Group**: `np.where(age < 18, 'Minor', np.where(age < 65, 'Adult', 'Senior'))`
- **Price Category**: `np.where(price < 50, 'Budget', np.where(price < 100, 'Mid-range', 'Premium'))`

### Date and Time

When working with datetime columns that have been properly converted:

- **Years Since**: `2025 - year`  # If you've extracted the year
- **Is Weekend**: `day_of_week > 5`  # If you've extracted day of week (0-6)

## Advanced Techniques

### Multiple Conditions

For more complex conditions, you can nest `np.where()` functions:

```
np.where(
    age < 18, 'Minor',
    np.where(
        age < 65, 'Adult',
        'Senior'
    )
)
```

### Binning Numeric Values

Create categories from numeric values:

```
np.where(
    score < 60, 'F',
    np.where(
        score < 70, 'D',
        np.where(
            score < 80, 'C',
            np.where(
                score < 90, 'B',
                'A'
            )
        )
    )
)
```

## Tips and Best Practices

1. **Start Simple**: Begin with simple expressions and build up complexity
2. **Check Data Types**: Ensure your columns are the correct data types before using them in expressions
3. **Handle Missing Values**: Be aware that missing values (NaN) can affect calculations
4. **Preview Results**: Always check the preview after adding a calculated column to ensure it worked as expected
5. **Avoid Division by Zero**: When dividing, consider adding a small value to the denominator or using conditional logic

## Troubleshooting

If your calculated column expression doesn't work:

1. Check that all column names are spelled correctly
2. Verify that columns used in the expression have the correct data types
3. Look for syntax errors in the expression
4. Try simpler expressions to isolate the problem
5. Consider handling special cases (like division by zero or missing values)

For more complex transformations, consider using the built-in data transformers or creating a custom data transformer plugin.
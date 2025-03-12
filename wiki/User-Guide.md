# User Guide

This guide provides detailed instructions on how to use DataFusion for merging and transforming files.

## Table of Contents

- [Interface Overview](#interface-overview)
- [Uploading Files](#uploading-files)
- [Merge Options](#merge-options)
- [Data Preview and Analysis](#data-preview-and-analysis)
- [Data Transformations](#data-transformations)
- [Exporting Data](#exporting-data)
- [Settings](#settings)

## Interface Overview

DataFusion has a clean, intuitive interface divided into several sections:

1. **Navigation Bar**: Switch between the File Merger and About pages
2. **Sidebar**: Contains settings, statistics, and help information
3. **Main Area**: Workflow sections for file uploading, options, and results
4. **Footer**: Additional information and links

## Uploading Files

To start merging files:

1. Navigate to the "File Merger" page if not already there
2. Click the "Choose files" button in the upload section
3. Select one or more files (CSV, Excel, or JSON)
4. The app will display the files you've uploaded

**Supported File Formats**:
- CSV (.csv)
- Excel (.xlsx, .xls)
- JSON (.json)

**Tips**:
- Files should have consistent column naming for best results
- Large files (>50MB) may take longer to process
- For CSV files with non-standard formats, you can specify delimiter and encoding in the advanced options

## Merge Options

After uploading files, configure how you want to merge them:

### Basic Merge Methods

- **Append (stack vertically)**: Stacks all files on top of each other
- **Join on key column (merge horizontally)**: Merges files side by side based on a key column
- **Smart merge (auto-detect)**: Automatically determines the best way to merge files

### Join Options

When using "Join on key column":

1. **Key Column**: Specify the column name that exists in all files
2. **Join Type**:
   - **Outer**: Keep all rows from all files (fill with NaN where needed)
   - **Inner**: Keep only rows that have matching keys in all files
   - **Left**: Keep all rows from the first file, join matching rows from other files

3. **Match Columns**: Enable to match columns with similar names across files

### Advanced Options

Expand the "Advanced Options" section to access:

- **Ignore case in column names**: Treat column names as case-insensitive
- **Remove duplicate rows**: Eliminate duplicate entries
- **Fill missing values**: Handle NaN values with various methods:
  - None (keep NaN)
  - Zero
  - Mean
  - Median
  - Mode
  - Forward fill
  - Backward fill
  - Custom value

### Output Filename

Specify a name for your output file (without extension).

## Data Preview and Analysis

After merging files, DataFusion provides several views of your data:

### Preview Table

- Displays the first 10 rows of your merged data
- Use the search/filter box to find specific data

### Data Analysis Tabs

1. **Column Information**: Details about each column (type, null counts, unique values)
2. **Data Types**: Columns grouped by data type
3. **Missing Values**: Analysis of missing data with visualization

## Data Transformations

Apply transformations to your merged data:

### Transformation Types

1. **Create calculated column**:
   - Specify a new column name
   - Enter an expression using existing column names as variables
   - Example: `revenue - cost` to calculate profit

2. **Convert data types**:
   - Select a column to convert
   - Choose target type (string, number, datetime, boolean)

3. **Replace values**:
   - Select a column
   - Specify the value to find
   - Enter the replacement value

4. **Filter rows**:
   - Select a column to filter on
   - Choose a filter type (equals, not equals, contains, greater than, less than)
   - Enter the filter value

### Reset Transformations

Click "Reset all transformations" to revert to the original merged dataset.

## Exporting Data

Export your merged and transformed data:

1. Select an export format (CSV, Excel, JSON)
2. Click the download button
3. If auto-download is enabled, the file will download automatically

### Download Information

The "Download Information" expander shows:
- Total records
- Total columns
- File name
- Notes about the selected format

## Settings

Access settings in the sidebar:

### Theme

Choose between Light and Dark themes.

### File Size Limit

Adjust the maximum allowed file size (10MB to 500MB).

### Help

The "Quick Tips" expander provides helpful reminders about key features.
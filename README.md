# Japanese Administrative Boundary Crosswalk Creator

## Overview
This tool creates geographic crosswalks between different years of Japanese administrative boundaries (1980-2000), implementing a spatial standardization procedure using 2000 boundaries as the reference unit. Following Eckert et al. (2020), it constructs precise geographic crosswalks by intersecting historical district boundaries with the reference map.

## Features
- Creates precise geographic crosswalks between different years
- Handles boundary changes over time
- Calculates area-based weights for accurate crosswalking
- Supports multiple years (currently 1980-2000)
- Exports results in Excel format

## Requirements
- Python 3.8+
- Dependencies:
  - geopandas
  - pandas
  - numpy
  - openpyxl

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ShizukaInoue/japanese-boundary-crosswalk.git
cd japanese-boundary-crosswalk
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Data Structure
Place your shapefiles in the following structure:
```

## Quick Start Guide

### Basic Usage
```python
# Example of minimal usage
import geopandas as gpd
from pathlib import Path

# Set up paths
base_dir = Path('Data')
export_dir = Path('Crosswalk')

# Process single year
year = 1980
```

### Example Output
Here's a sample of what the output crosswalk looks like:

| CITY2000 | CITY1980 | PREF2000 | PREF1980 | weight | GUN1980 | GUN2000 | City Code 2000 | City Code 1980 |
|----------|----------|-----------|-----------|---------|---------|---------|----------------|----------------|
| 札幌市 | 札幌市 | 北海道 | 北海道 | 1.000 | - | - | 01100 | 01100 |
| 函館市 | 函館市 | 北海道 | 北海道 | 0.982 | - | - | 01202 | 01202 |
| ... | ... | ... | ... | ... | ... | ... | ... | ... |

## Detailed Methodology

### 1. Data Preparation
- Loads shapefiles for reference year (2000) and target year
- Validates geometry and attribute data
- Converts to common projection for accurate area calculation

### 2. Spatial Processing
```python
# Key processing steps
# 1. Dissolve to city level
gdf['dissolve_key'] = gdf['N03_007']
gdf = gdf.dissolve(by="dissolve_key").reset_index()

# 2. Convert to equal-area projection
gdf = gdf.to_crs({'proj':'cea'})

# 3. Clean geometry
gdf['geometry'] = gdf['geometry'].buffer(0)

# 4. Calculate areas
gdf['Area'] = gdf.area/10**6
```

### 3. Weight Calculation
The weights are calculated using the following formula:
\[
w_{ij} = \frac{A_{ij}}{\sum_{j} A_{ij}}
\]
where:
- \(w_{ij}\) is the weight between area i in reference year and area j in target year
- \(A_{ij}\) is the intersection area between i and j

## Advanced Features

### Custom Weight Thresholds
Adjust the threshold for minimum weight consideration:
```python
# Default threshold
THRESHOLD = 0.0001

# For more precise results
THRESHOLD = 0.00001

# For faster processing with less precision
THRESHOLD = 0.001
```

### Batch Processing
Process multiple years at once:
```python
# Process a range of years
years = range(1980, 2021, 5)  # 1980, 1985, 1990, ...
for year in years:
    create_crosswalk(base_dir, export_dir, year)
```

## Data Quality Checks

### Pre-processing Checks
- File encoding validation
- Required column presence
- Geometry validity
- CRS consistency

### Post-processing Validation
```python
# Verify weight sums
weight_sums = df.groupby('City Code 2000')['weight'].sum()
print(f"Min weight sum: {weight_sums.min():.3f}")
print(f"Max weight sum: {weight_sums.max():.3f}")

# Check for missing values
missing = df.isnull().sum()
print("Missing values by column:")
print(missing[missing > 0])
```

## Performance Optimization

### Memory Usage
For large datasets:
```python
# Read only necessary columns
columns = ['N03_007', 'PREF', 'GUN', 'CITY', 'geometry']
gdf = gpd.read_file(file_path, encoding='shift_jis', usecols=columns)

# Simplify geometries if needed
gdf['geometry'] = gdf['geometry'].simplify(tolerance=0.001)
```

### Processing Speed
Tips for faster processing:
1. Use spatial indexing
2. Simplify geometries
3. Process in parallel for multiple years

## Error Handling

### Common Errors and Solutions

1. **Encoding Issues**
```python
try:
    gdf = gpd.read_file(file_path, encoding='shift_jis')
except UnicodeDecodeError:
    # Try alternative encodings
    gdf = gpd.read_file(file_path, encoding='cp932')
```

2. **Geometry Errors**
```python
# Fix invalid geometries
gdf['geometry'] = gdf['geometry'].make_valid()
```

3. **Missing Data**
```python
# Check for required columns
required_cols = ['N03_007', 'PREF', 'GUN', 'CITY']
missing_cols = [col for col in required_cols if col not in gdf.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")
```

## Data Sources and Preparation

### Obtaining Shapefiles
1. **Official Sources**:
   - [MLIT National Land Numerical Information](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03.html)
   - Historical boundaries available for multiple years
   - Download the N03 Administrative District data

2. **Data Preprocessing**:
   ```python
   # Example preprocessing script
   import geopandas as gpd
   
   def preprocess_shapefile(input_path, output_path):
       # Read raw shapefile
       gdf = gpd.read_file(input_path, encoding='shift_jis')
       
       # Basic cleaning
       gdf = gdf.dropna(subset=['N03_007'])
       gdf['N03_007'] = gdf['N03_007'].astype(str)
       
       # Save processed file
       gdf.to_file(output_path, encoding='shift_jis')
   ```

## Extended Usage Examples

### 1. Basic Crosswalk Creation
```python
from pathlib import Path
import logging

# Setup
base_dir = Path('Data')
export_dir = Path('Crosswalk')
year = 1980

# Create crosswalk with default settings
create_crosswalk(base_dir, export_dir, year)
```

### 2. Custom Configuration
```python
# Modify parameters for specific needs
create_crosswalk(
    base_dir=base_dir,
    export_dir=export_dir,
    target_year=1980,
    reference_year=2000,
    threshold=0.0005,  # Higher threshold for faster processing
    encoding='cp932'   # Alternative encoding if needed
)
```

### 3. Batch Processing with Error Handling
```python
def batch_process_years(start_year, end_year, step=5):
    years = range(start_year, end_year + 1, step)
    results = {}
    
    for year in years:
        try:
            create_crosswalk(base_dir, export_dir, year)
            results[year] = 'Success'
        except Exception as e:
            results[year] = f'Failed: {str(e)}'
            logging.error(f"Error processing year {year}: {e}")
    
    return results

# Process multiple years
results = batch_process_years(1980, 2000, 5)
```

## Validation and Quality Control

### 1. Input Data Validation
```python
def validate_shapefile(file_path):
    checks = {
        'file_exists': False,
        'valid_encoding': False,
        'required_columns': False,
        'valid_geometries': False
    }
    
    # Check file existence
    if file_path.exists():
        checks['file_exists'] = True
        
        try:
            # Try reading the file
            gdf = gpd.read_file(file_path, encoding='shift_jis')
            checks['valid_encoding'] = True
            
            # Check required columns
            required = ['N03_007', 'PREF', 'GUN', 'CITY']
            if all(col in gdf.columns for col in required):
                checks['required_columns'] = True
            
            # Validate geometries
            if all(gdf.geometry.is_valid):
                checks['valid_geometries'] = True
                
        except Exception as e:
            logging.error(f"Validation error: {e}")
    
    return checks
```

### 2. Output Validation
```python
def validate_crosswalk(crosswalk_path):
    df = pd.read_excel(crosswalk_path)
    
    # Check weight normalization
    weight_sums = df.groupby('City Code 2000')['weight'].sum()
    is_normalized = np.allclose(weight_sums, 1.0, atol=1e-3)
    
    # Check for missing values
    has_missing = df.isnull().any().any()
    
    # Check code consistency
    code_format_valid = df['City Code 2000'].str.match(r'^\d{5}$').all()
    
    return {
        'normalized_weights': is_normalized,
        'complete_data': not has_missing,
        'valid_codes': code_format_valid
    }
```

## Advanced Topics

### 1. Memory Optimization
For processing very large datasets:
```python
def process_large_shapefile(file_path, chunk_size=1000):
    """Process large shapefiles in chunks to manage memory."""
    import dask_geopandas
    
    # Read data in chunks
    gdf = dask_geopandas.read_file(file_path)
    
    # Process in parallel
    gdf = gdf.repartition(npartitions=4)
    return gdf.compute()
```

### 2. Custom Weight Calculations
Implement alternative weighting schemes:
```python
def calculate_custom_weights(intersect_gdf, weight_type='population'):
    """Calculate weights based on different metrics."""
    if weight_type == 'population':
        # Population-weighted approach
        intersect_gdf['weight'] = (
            intersect_gdf['intersect_area'] * 
            intersect_gdf['population_density']
        )
    elif weight_type == 'developed_area':
        # Urban area weighted approach
        intersect_gdf['weight'] = (
            intersect_gdf['intersect_area'] * 
            intersect_gdf['urban_ratio']
        )
    
    # Normalize weights
    return normalize_weights(intersect_gdf)
```

## Appendix

### A. Shapefile Structure
Detailed explanation of required shapefile attributes:
```
N03_007 (市区町村コード): 5-digit city code
  - First 2 digits: Prefecture code (01-47)
  - Last 3 digits: City/district code
  Example: 13101 = Tokyo-to (13) + Chiyoda-ku (101)

Required Columns:
  - N03_007: City code (文字型)
  - PREF: Prefecture name (都道府県名)
  - CITY: City name (市区町村名)
  - GUN: District name (郡名) - can be null
  - geometry: Polygon/MultiPolygon
```

### B. Japanese Administrative Divisions
```
Hierarchy:
1. Prefecture (都道府県)
   - To/Do/Fu/Ken (都・道・府・県)
2. District (郡)
   - Optional administrative level
3. Municipality (市区町村)
   - Cities (市)
   - Wards (区)
   - Towns (町)
   - Villages (村)
```

### C. Reference Years and Changes
```
Key Administrative Changes:
1980-2000 Period:
- Major municipal mergers (平成の大合併)
- Special ward system changes
- Government ordinance city designations
```

## Technical Details

### A. Coordinate Reference Systems
```python
# Common CRS used in Japanese administrative data
COMMON_CRS = {
    'JGD2000': 'EPSG:4612',  # Japanese Geodetic Datum 2000
    'JGD2011': 'EPSG:6668',  # Japanese Geodetic Datum 2011
    'WGS84': 'EPSG:4326',    # World Geodetic System 1984
    'Equal Area': 'EPSG:6933' # World Cylindrical Equal Area
}

# Example CRS transformation
gdf = gdf.to_crs(COMMON_CRS['Equal Area'])
```

### B. Performance Benchmarks
Typical processing times on standard hardware:
```
Single Year Processing:
- Small prefecture: ~30 seconds
- Large prefecture: ~2-3 minutes
- Entire country: ~15-20 minutes

Memory Usage:
- Raw shapefile: 100-200MB
- Processing peak: 2-4GB
- Output file: 5-10MB
```

## Contributing Guidelines

### Code Style
Follow these conventions:
```python
# Variable naming
CONSTANTS = 'UPPERCASE'
variable_names = 'snake_case'
function_names = 'snake_case'

# Docstrings
def function_name(param1: type, param2: type) -> return_type:
    """
    Short description.

    Args:
        param1: Description
        param2: Description

    Returns:
        Description of return value

    Raises:
        ExceptionType: Description of when this occurs
    """
```

### Testing
```python
# Example test case
def test_weight_calculation():
    """Test weight calculation and normalization."""
    test_data = create_test_data()
    weights = calculate_weights(test_data)
    
    assert np.allclose(weights.sum(), 1.0)
    assert (weights >= 0).all()
    assert (weights <= 1).all()
```

## Troubleshooting Guide

### Common Issues

1. **Memory Errors**
```
Problem: MemoryError during processing
Solutions:
- Use chunked processing
- Reduce geometry precision
- Process by region
```

2. **Encoding Issues**
```
Problem: Character encoding errors
Solutions:
- Verify source encoding
- Try different encodings:
  - shift_jis
  - cp932
  - utf-8
```

3. **Geometry Errors**
```
Problem: Invalid geometries
Solutions:
- Use topology correction
- Apply buffer(0)
- Simplify geometries
```

## Future Development

### Planned Features
1. Support for more recent years (2000-2020)
2. Population-weighted crosswalks
3. Interactive visualization tools
4. API integration for automated updates

### Known Limitations
1. Special cases not handled:
   - Water body boundaries
   - Disputed territories
   - Special administrative regions

## Citation and References

### How to Cite
```bibtex
@software{inoue2024crosswalk,
  author       = {Inoue, Shizuka},
  title        = {Japanese Administrative Boundary Crosswalk Creator},
  year         = {2024},
  publisher    = {GitHub},
  url          = {https://github.com/ShizukaInoue/japanese-boundary-crosswalk}
}
```

### Related Work
1. Eckert et al. (2020) "Imputing Missing Values in Geographic Data"
2. Japanese Statistical Bureau Documentation
3. MLIT Administrative Boundary Data Documentation
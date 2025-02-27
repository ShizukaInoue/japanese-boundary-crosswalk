# Japanese Administrative Boundary Crosswalk Creator

Creates a template for geographic crosswalks between different years of Japanese administrative boundaries.

## Overview

This tool helps track changes in Japanese administrative boundaries over time by:
- Creating crosswalks between different years
- Calculating area-based weights
- Handling boundary changes and mergers
- Exporting results in Excel format

## Requirements

- Python 3.8+
- Required packages:
  ```
  geopandas
  pandas
  numpy
  openpyxl
  ```

## Data Structure

Place your shapefiles in this structure:
```
Data/
├── jpn1980/
│   └── jpn1980geo.shp (+ associated files)
└── jpn2000/
    └── jpn2000geo.shp (+ associated files)
```

Required columns in shapefiles:
- N03_007: City code (5 digits)
- PREF: Prefecture name
- CITY: City name
- GUN: District name
- geometry: Polygon/MultiPolygon

## Usage

This package provides tools to create crosswalks between different years of Japanese administrative boundaries. There are two ways to use this tool:

### Option 1: Using the direct runner script (Recommended)

The simplest way to run the crosswalk creator is to use the `direct_run.py` script, which is self-contained and doesn't require package installation:

```bash
python direct_run.py --source-year 2000 --target-year 1980
```

### Option 2: Using the package

You can also install the package and use it as a Python module:

```bash
# Install the package in development mode
pip install -e .

# Run the main script
python main.py --source-year 2000 --target-year 1980
```

### Command-line Arguments

Both scripts accept the following arguments:

- `--source-year`: Year of source boundaries (default: 2000)
- `--target-year`: Year of target boundaries (default: 1980)
- `--source-path`: Path to source shapefile (optional)
- `--target-path`: Path to target shapefile (optional)
- `--output-path`: Path to save crosswalk (optional)
- `--weight-threshold`: Minimum weight to include in crosswalk (default: 0.001)

### Data Requirements

The tool expects shapefiles in the following locations:
- `Data/jpn{source_year}/jpn{source_year}geo.shp`
- `Data/jpn{target_year}/jpn{target_year}geo.shp`

The shapefiles must contain the following columns:
- `PREF`: Prefecture name
- `CITY`: City name
- `GUN`: District name (optional)
- `N03_007`: City code (optional)

### Output

The crosswalk is saved as an Excel file at:
- `Crosswalk/Crosswalk_{source_year}_{target_year}.xlsx`

The Excel file contains the following columns:
- `PREF{source_year}/PREF{target_year}`: Prefecture names
- `CITY{source_year}/CITY{target_year}`: City names
- `GUN{source_year}/GUN{target_year}`: District names
- `City Code {source_year}/{target_year}`: 5-digit administrative codes
- `weight`: Area-based weight for crosswalking

## Weight Calculation

The crosswalk standardizes all city-level data to 2000 city definitions. Following Eckert et al. (2020), we:
1. Intersect historical city boundaries with 2000 boundaries
2. Create subunits based on these intersections
3. Reallocate variables proportionally based on area overlap

### Methodology

For a given historical year, weights are calculated as:

$$
w_{ij} = \frac{A_{ij}}{A_j^{hist}} \quad \forall i \in \mathcal{I}, j \in \mathcal{J}
$$

where:
- $w_{ij}$ is the weight between city $i$ in 2000 and city $j$ in the reference year
- $A_{ij}$ is the intersection area between cities $i$ and $j$
- $A_j^{hist}$ is the total area of historical city $j$
- $\mathcal{I}$ is the set of 1980 cities (reference)
- $\mathcal{J}$ is the set of historical cities

### Usage Example

For a historical (1980) variable $X$ (e.g., population), its value in 2000 boundaries is:

$$
X_i^{2000} = \sum_{j \in \mathcal{J}} w_{ij} X_j^{1980}
$$

For example, consider a 2000 city i that overlaps with two 1980 cities:

| 1980 City ($\mathcal{J}$) | Population ($X_j$)| Area Overlap with 2000 City i ($w_{ij}$)|
|-----------|------------|------------------------------|
| City A    | 100       | 20% of City A's area        |
| City B    | 10        | 100% of City B's area       |

The 1980 population for 2000 city i would be:
$$X_i^{2000} = (100 \times 0.2) + (10 \times 1.0) = 30$$

This means that based on area-weighted reallocation, 30 people from 1980 would be assigned to the 2000 boundaries of city i.

### Important Notes

1. Variables are reallocated proportionally to area overlap
2. Best suited for stock variables (e.g., population, casualties)
3. Weights represent the fraction of historical city area that overlaps with 1980 cities
4. More disaggregated historical data provides better accuracy

## References

Eckert, F., Gvirtz, A., Liang, J., & Peters, M. (2020). "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790." [Working Paper](https://fpeckert.me/eglp/).

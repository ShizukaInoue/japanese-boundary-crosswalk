# Japanese Administrative Boundary Crosswalk Creator

Creates geographic crosswalks between different years of Japanese administrative boundaries (1980-2000), using 2000 boundaries as the reference unit.

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

1. Place shapefiles in the `Data` directory
2. Run the notebook:
```python
# Basic usage
import geopandas as gpd
from pathlib import Path

# Set up paths
base_dir = Path('Data')
export_dir = Path('Crosswalk')

# Process single year
year = 1980
```

## Output

Creates Excel files with crosswalk information:
```
Crosswalk/
└── Crosswalk_2000_1980.xlsx
```

Sample output format:

| CITY2000 | CITY1980 | PREF2000 | PREF1980 | GUN2000 | GUN1980 | City Code 2000 | City Code 1980 | weight |
|----------|----------|-----------|-----------|---------|---------|----------------|----------------|---------|
| 札幌市 | 札幌市 | 北海道 | 北海道 | - | - | 01100 | 01100 | 1.000 |
| 函館市 | 函館市 | 北海道 | 北海道 | - | - | 01202 | 01202 | 0.982 |
| 江別市 | 江別町 | 北海道 | 北海道 | - | 石狩郡 | 01217 | 01303 | 0.995 |
| 八雲町 | 八雲町 | 北海道 | 北海道 | 二海郡 | 山越郡 | 01345 | 01371 | 0.873 |
| 余市町 | 余市町 | 北海道 | 北海道 | 余市郡 | 余市郡 | 01423 | 01423 | 1.000 |

Notes on output:
- CITY2000/CITY1980: City names in respective years
- PREF2000/PREF1980: Prefecture names
- GUN2000/GUN1980: District names (if applicable)
- City Code: 5-digit administrative codes (first 2 digits: prefecture code)
- weight: Area-based weight for crosswalking (sum to 1 for each 2000 unit)

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

| 1980 City $\mathcal{J}$ | Population (X_j)| Area Overlap with 2000 City i ($w_{ij}$)|
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

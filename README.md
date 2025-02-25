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

The crosswalk weights are calculated using the following methodology:

Let $\mathcal{I}$ be the set of administrative units in 2000 and $\mathcal{J}$ be the set of units in the target year. The weight between units is:

$$
w_{ij} = \frac{A_{ij}}{\sum_{j \in \mathcal{J}} A_{ij}}
$$

where:
- $w_{ij}$ is the weight between unit $i$ in 2000 and unit $j$ in target year
- $A_{ij}$ is the intersection area between units $i$ and $j$

The intersection area is calculated as:

$$
A_{ij} = \text{Area}(G_i \cap G_j)
$$

where:
- $G_i$ is the geometry of unit $i$ in 2000
- $G_j$ is the geometry of unit $j$ in target year
- $\cap$ denotes geometric intersection

Properties of weights:
1. Non-negativity: $w_{ij} \geq 0$
2. Sum to unity: $\sum_{j} w_{ij} = 1$
3. Threshold filter: $w_{ij} = 0$ if $\frac{A_{ij}}{A_i} < 10^{-4}$

## References

Eckert et al. (2020) "A Method to Construct Geographical Crosswalks with an Application to US Counties since 1790" 
https://fpeckert.me/eglp/

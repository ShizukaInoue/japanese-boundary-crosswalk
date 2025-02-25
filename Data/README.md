# Data Directory

This directory should contain the Japanese administrative boundary shapefiles.

## Required Files

```
Data/
├── jpn1980/
│   └── jpn1980geo.shp (+ associated files)
└── jpn2000/
    └── jpn2000geo.shp (+ associated files)
```

## Data Sources

The shapefiles can be obtained from:
1. MLIT National Land Numerical Information download service (国土数値情報ダウンロードサービス)
   - URL: https://nlftp.mlit.go.jp/ksj/
   - Navigate to: 政策区域 > 行政区域
   - Download the relevant years (1980, 2000)

2. Required processing:
   - Extract downloaded files
   - Ensure column names match requirements (N03_007, PREF, CITY, GUN)
   - Place in appropriate year subdirectories 
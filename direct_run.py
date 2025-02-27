#!/usr/bin/env python3
"""
Direct runner for the Japanese Administrative Boundary Crosswalk Creator.

This script directly imports and runs the code without relying on package imports.
"""

import os
import sys
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path

# Get the absolute path of the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))

# Define utility functions
def load_shapefiles(
    source_year=2000,
    target_year=1980,
    source_path=None,
    target_path=None
):
    """Load source and target shapefiles."""
    # Get the project root directory
    project_root = Path(current_dir)
    
    # Set default paths if not provided
    if source_path is None:
        source_path = project_root / f"Data/jpn{source_year}/jpn{source_year}geo.shp"
    
    if target_path is None:
        target_path = project_root / f"Data/jpn{target_year}/jpn{target_year}geo.shp"
    
    # Check if files exist
    if not source_path.exists():
        raise FileNotFoundError(f"Source shapefile not found: {source_path}")
    
    if not target_path.exists():
        raise FileNotFoundError(f"Target shapefile not found: {target_path}")
    
    # Load shapefiles
    print(f"Loading {source_year} shapefile from {source_path}...")
    source_gdf = gpd.read_file(source_path)
    
    print(f"Loading {target_year} shapefile from {target_path}...")
    target_gdf = gpd.read_file(target_path)
    
    # Validate required columns
    required_cols = ['PREF', 'CITY']
    for col in required_cols:
        if col not in source_gdf.columns:
            raise ValueError(f"Column '{col}' not found in source shapefile")
        if col not in target_gdf.columns:
            raise ValueError(f"Column '{col}' not found in target shapefile")
    
    # Add year suffix to columns
    source_gdf = source_gdf.rename(columns={
        'PREF': f'PREF{source_year}',
        'CITY': f'CITY{source_year}',
        'GUN': f'GUN{source_year}' if 'GUN' in source_gdf.columns else None,
    })
    
    target_gdf = target_gdf.rename(columns={
        'PREF': f'PREF{target_year}',
        'CITY': f'CITY{target_year}',
        'GUN': f'GUN{target_year}' if 'GUN' in target_gdf.columns else None,
    })
    
    return source_gdf, target_gdf

def save_crosswalk(crosswalk, output_path):
    """Save crosswalk to Excel file."""
    # If output_path is not absolute, make it relative to project root
    if not output_path.is_absolute():
        project_root = Path(current_dir)
        output_path = project_root / output_path
    
    # Create directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Saving crosswalk to {output_path}...")
    crosswalk.to_excel(output_path, index=False)
    print(f"Saved crosswalk with {len(crosswalk)} rows.")

def calculate_intersections(
    source_gdf,
    target_gdf,
    source_year,
    target_year
):
    """Calculate intersections between source and target geometries."""
    try:
        # Create spatial index for faster intersection
        target_sindex = target_gdf.sindex
        
        # Initialize lists to store results
        intersections_list = []
        
        # Process each source geometry
        total = len(source_gdf)
        for idx, source_row in enumerate(source_gdf.itertuples()):
            if idx % 100 == 0 or idx == total - 1:
                print(f"Processing {idx+1}/{total} source geometries...")
            
            # Get potential intersections using spatial index
            possible_matches_idx = list(target_sindex.intersection(source_row.geometry.bounds))
            possible_matches = target_gdf.iloc[possible_matches_idx]
            
            # Calculate actual intersections
            for target_idx, target_row in possible_matches.iterrows():
                if source_row.geometry.intersects(target_row.geometry):
                    intersection = source_row.geometry.intersection(target_row.geometry)
                    
                    # Skip empty intersections
                    if intersection.is_empty:
                        continue
                    
                    # Calculate area
                    intersection_area = intersection.area
                    
                    # Skip very small intersections (likely due to precision issues)
                    if intersection_area <= 1e-10:
                        continue
                    
                    # Create record
                    record = {
                        f"PREF{source_year}": getattr(source_row, f"PREF{source_year}", ""),
                        f"CITY{source_year}": getattr(source_row, f"CITY{source_year}", ""),
                        f"GUN{source_year}": getattr(source_row, f"GUN{source_year}", ""),
                        f"City Code {source_year}": getattr(source_row, "N03_007", ""),
                        f"PREF{target_year}": getattr(target_row, f"PREF{target_year}", ""),
                        f"CITY{target_year}": getattr(target_row, f"CITY{target_year}", ""),
                        f"GUN{target_year}": getattr(target_row, f"GUN{target_year}", ""),
                        f"City Code {target_year}": getattr(target_row, "N03_007", ""),
                        "intersection_area": intersection_area,
                        "geometry": intersection
                    }
                    
                    intersections_list.append(record)
        
        if not intersections_list:
            print("Warning: No intersections found.")
            return gpd.GeoDataFrame([], crs=source_gdf.crs)
        
        # Create GeoDataFrame from results
        intersections_gdf = gpd.GeoDataFrame(intersections_list, crs=source_gdf.crs)
        
        print(f"Found {len(intersections_gdf)} intersections.")
        return intersections_gdf
        
    except Exception as e:
        print(f"Error calculating intersections: {str(e)}")
        raise

def calculate_weights(
    intersections,
    source_gdf,
    target_gdf,
    source_year,
    target_year
):
    """Calculate weights for each intersection based on area."""
    try:
        # Create dictionaries for area lookup
        source_areas = {}
        for idx, row in source_gdf.iterrows():
            key = row[f"CITY{source_year}"]
            source_areas[key] = row.geometry.area
        
        target_areas = {}
        for idx, row in target_gdf.iterrows():
            key = row[f"CITY{target_year}"]
            target_areas[key] = row.geometry.area
        
        # Calculate weights
        # Weight = intersection area / target area (historical area)
        intersections['source_area'] = intersections[f'CITY{source_year}'].map(source_areas)
        intersections['target_area'] = intersections[f'CITY{target_year}'].map(target_areas)
        
        # Check for missing areas
        missing_source = intersections[intersections['source_area'].isna()]
        missing_target = intersections[intersections['target_area'].isna()]
        
        if not missing_source.empty:
            print(f"Warning: {len(missing_source)} source cities not found in area lookup.")
        
        if not missing_target.empty:
            print(f"Warning: {len(missing_target)} target cities not found in area lookup.")
        
        # Calculate weight as intersection area / target area (historical area)
        intersections['weight'] = intersections['intersection_area'] / intersections['target_area']
        
        # Check for invalid weights
        invalid_weights = intersections[~np.isfinite(intersections['weight'])]
        if not invalid_weights.empty:
            print(f"Warning: {len(invalid_weights)} rows have invalid weights (NaN or Inf).")
            # Set invalid weights to 0
            intersections.loc[~np.isfinite(intersections['weight']), 'weight'] = 0
        
        # Drop geometry column for final dataframe
        crosswalk = intersections.drop(columns=['geometry', 'intersection_area', 'source_area', 'target_area'])
        
        return crosswalk
        
    except Exception as e:
        print(f"Error calculating weights: {str(e)}")
        raise

def create_crosswalk(
    source_year=2000,
    target_year=1980,
    source_path=None,
    target_path=None,
    output_path=None,
    weight_threshold=0.001,
):
    """Create a crosswalk between two years of Japanese administrative boundaries."""
    try:
        # Load shapefiles
        source_gdf, target_gdf = load_shapefiles(source_year, target_year, source_path, target_path)
        
        # Ensure CRS match
        if source_gdf.crs != target_gdf.crs:
            print(f"CRS mismatch: {source_gdf.crs} vs {target_gdf.crs}")
            print(f"Converting target CRS to match source...")
            target_gdf = target_gdf.to_crs(source_gdf.crs)
        
        # Calculate intersections
        print(f"Calculating intersections between {source_year} and {target_year} boundaries...")
        intersections = calculate_intersections(source_gdf, target_gdf, source_year, target_year)
        
        if len(intersections) == 0:
            print("Warning: No intersections found between source and target boundaries.")
            return pd.DataFrame()
        
        # Calculate weights
        print("Calculating weights...")
        crosswalk = calculate_weights(intersections, source_gdf, target_gdf, source_year, target_year)
        
        # Filter by threshold
        original_count = len(crosswalk)
        crosswalk = crosswalk[crosswalk['weight'] > weight_threshold].copy()
        filtered_count = len(crosswalk)
        
        if filtered_count < original_count:
            print(f"Filtered out {original_count - filtered_count} rows with weight <= {weight_threshold}")
        
        # Set default output path if not provided
        if output_path is None:
            project_root = Path(current_dir)
            output_path = project_root / f"Crosswalk/Crosswalk_{source_year}_{target_year}.xlsx"
        
        # Save crosswalk
        save_crosswalk(crosswalk, output_path)
        
        return crosswalk
        
    except Exception as e:
        print(f"Error creating crosswalk: {str(e)}")
        raise

def main():
    """Main entry point for the crosswalk creator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Create crosswalks between Japanese administrative boundaries"
    )
    
    parser.add_argument(
        "--source-year",
        type=int,
        default=2000,
        help="Year of source boundaries (default: 2000)"
    )
    
    parser.add_argument(
        "--target-year",
        type=int,
        default=1980,
        help="Year of target boundaries (default: 1980)"
    )
    
    parser.add_argument(
        "--source-path",
        type=Path,
        help="Path to source shapefile (default: Data/jpn{source_year}/jpn{source_year}geo.shp)"
    )
    
    parser.add_argument(
        "--target-path",
        type=Path,
        help="Path to target shapefile (default: Data/jpn{target_year}/jpn{target_year}geo.shp)"
    )
    
    parser.add_argument(
        "--output-path",
        type=Path,
        help="Path to save crosswalk (default: Crosswalk/Crosswalk_{source_year}_{target_year}.xlsx)"
    )
    
    parser.add_argument(
        "--weight-threshold",
        type=float,
        default=0.001,
        help="Minimum weight to include in crosswalk (default: 0.001)"
    )
    
    args = parser.parse_args()
    
    print(f"Creating crosswalk between {args.source_year} and {args.target_year}...")
    
    try:
        # Create crosswalk
        crosswalk = create_crosswalk(
            source_year=args.source_year,
            target_year=args.target_year,
            source_path=args.source_path,
            target_path=args.target_path,
            output_path=args.output_path,
            weight_threshold=args.weight_threshold
        )
        
        print(f"Created crosswalk with {len(crosswalk)} rows")
    except FileNotFoundError as e:
        print(f"Error: {str(e)}")
        print("\nMake sure you have the required shapefiles in the Data directory:")
        print(f"- Data/jpn{args.source_year}/jpn{args.source_year}geo.shp")
        print(f"- Data/jpn{args.target_year}/jpn{args.target_year}geo.shp")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 
#!/usr/bin/env python3
"""
Japanese Administrative Boundary Crosswalk Creator

Command-line interface for creating crosswalks between different years
of Japanese administrative boundaries.
"""

import argparse
import os
import sys
from pathlib import Path

# Add the parent directory to sys.path to ensure crosswalk can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crosswalk import create_crosswalk


def main():
    """Main entry point for the crosswalk creator."""
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


if __name__ == "__main__":
    main() 
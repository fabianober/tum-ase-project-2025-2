#!/usr/bin/env python3
"""
Composite Stress Data Extraction Script

This script extracts composite stress data from a .cstr file (composite results file)
and exports it to a CSV file. It specifically extracts:
- NORMAL-1 stress values
- NORMAL-2 stress values  
- SHEAR-12 stress values

For BOT and TOP locations only, ordered by Element ID and Ply ID.

Author: Generated for ASE Project
Date: 2025
"""

import re
import pandas as pd
import os
import sys

def extract_composite_stresses(input_file, output_file):
    """
    Extract composite stress data from .cstr file and save to CSV.
    
    Args:
        input_file (str): Path to the .cstr input file
        output_file (str): Path to the output CSV file
        
    Returns:
        pandas.DataFrame: DataFrame containing the extracted stress data
    """
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return None
    
    # List to store extracted data
    stress_data = []
    
    try:
        # Read the file
        with open(input_file, 'r') as f:
            lines = f.readlines()

        # State variables
        in_stress_section = False
        current_element = None

        # Process each line
        for i, line in enumerate(lines):
            # Check if we're entering a stress section
            if "S T R E S S E S   I N   L A Y E R E D   C O M P O S I T E  E L E M E N T S" in line:
                in_stress_section = True
                continue

            # Check if we're entering a strain section (to stop processing stresses)
            if "S T R A I N S   I N   L A Y E R E D   C O M P O S I T E  E L E M E N T S" in line:
                in_stress_section = False
                continue

            # Only process lines in stress sections
            if not in_stress_section:
                continue

            # Skip header lines
            if "ELEMENT" in line and "PLY" in line and "LOC" in line:
                continue

            # Match element data line (starts with element ID)
            element_match = re.match(r'^\s*(\d+)\s+(\d+)\s+(BOT|TOP|MID)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)', line)
            if element_match:
                element_id = int(element_match.group(1))
                ply_id = int(element_match.group(2))
                location = element_match.group(3)
                normal_1 = float(element_match.group(4))
                normal_2 = float(element_match.group(5))
                shear_12 = float(element_match.group(6))

                current_element = element_id

                # Only keep BOT and TOP locations
                if location in ['BOT', 'TOP']:
                    stress_data.append({
                        'Element_ID': element_id,
                        'Ply_ID': ply_id,
                        'Location': location,
                        'Normal_1': normal_1,
                        'Normal_2': normal_2,
                        'Shear_12': shear_12
                    })
                continue

            # Match continuation lines (ply data for the same element)
            ply_match = re.match(r'^\s+(\d+)\s+(BOT|TOP|MID)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)', line)
            if ply_match and current_element is not None:
                ply_id = int(ply_match.group(1))
                location = ply_match.group(2)
                normal_1 = float(ply_match.group(3))
                normal_2 = float(ply_match.group(4))
                shear_12 = float(ply_match.group(5))

                # Only keep BOT and TOP locations
                if location in ['BOT', 'TOP']:
                    stress_data.append({
                        'Element_ID': current_element,
                        'Ply_ID': ply_id,
                        'Location': location,
                        'Normal_1': normal_1,
                        'Normal_2': normal_2,
                        'Shear_12': shear_12
                    })
                continue

            # Match location continuation lines (just location and values)
            location_match = re.match(r'^\s+(BOT|TOP|MID)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)\s+(-?\d+\.\d+E[+-]\d+)', line)
            if location_match and current_element is not None:
                location = location_match.group(1)
                normal_1 = float(location_match.group(2))
                normal_2 = float(location_match.group(3))
                shear_12 = float(location_match.group(4))

                # Only keep BOT and TOP locations
                if location in ['BOT', 'TOP']:
                    # Get the most recent ply ID for this element
                    recent_ply = None
                    for j in range(len(stress_data) - 1, -1, -1):
                        if stress_data[j]['Element_ID'] == current_element:
                            recent_ply = stress_data[j]['Ply_ID']
                            break

                    if recent_ply is not None:
                        stress_data.append({
                            'Element_ID': current_element,
                            'Ply_ID': recent_ply,
                            'Location': location,
                            'Normal_1': normal_1,
                            'Normal_2': normal_2,
                            'Shear_12': shear_12
                        })

        # Create DataFrame
        df = pd.DataFrame(stress_data)

        if df.empty:
            print("Warning: No stress data was extracted from the file.")
            return None

        # Remove duplicates if any
        initial_count = len(df)
        df = df.drop_duplicates()
        if len(df) < initial_count:
            print(f"Removed {initial_count - len(df)} duplicate entries.")

        # Sort by Element ID, Ply ID, and Location
        df = df.sort_values(['Element_ID', 'Ply_ID', 'Location'])

        # Reset index
        df = df.reset_index(drop=True)

        # Save to CSV
        df.to_csv(output_file, index=False)

        return df

    except Exception as e:
        print(f"Error processing file: {e}")
        return None

def main():
    """Main function to run the extraction."""
    
    # Define file paths
    input_file = "E04_ASE2_SS25_Double_Stringer_Panel.cstr"
    output_file = "composite_stresses.csv"

    # Check if we're in the right directory
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found in current directory.")
        print("Please make sure you're running this script from the directory containing the .cstr file.")
        print(f"Current directory: {os.getcwd()}")
        return 1

    # Extract the data
    df = extract_composite_stresses(input_file, output_file)

    if df is not None and not df.empty:
        return 0
    else:
        print(f"ERROR: No data was extracted.")
        print(f"Please check the input file format.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

import csv
import os

def total_mass(name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, '..', 'data', name, 'properties', 'element_masses.csv')
    total_mass = 0.0
    exclude_elements = {'31', '32', '33', '34', '35', '36'}
    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row.get('elements') not in exclude_elements:
                total_mass += float(row['mass'])
    
    total_mass = round(total_mass *1000, 3)
    return total_mass  # Convert tonns to kg

def write_mass_to_file(name):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = os.path.join(base_dir, '..', 'data', name, 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'mass.txt')
    with open(output_path, 'w') as f:
        f.write(f"{total_mass(name)}")
    return True

if __name__ == "__main__":
    mass = total_mass('fabian')
    print(f"Total mass: {mass}")
    print(write_mass_to_file('fabian'))